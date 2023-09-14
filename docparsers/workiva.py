from bs4 import BeautifulSoup
from typing import List, Dict

from .docparsertypes import ParserReturn


class WorkivaParser:

    def parse(self, dom : BeautifulSoup) -> List[str]:
        string_elts = []
        structured_data = []
        
        stack = [dom]
        context_dict = {}

        while len(stack):
            elt = stack.pop()

            if elt.name is None:
                s = elt.get_text().strip()
                if s:
                    string_elts.append(s)
                continue

            if elt.name == 'header' and elt.prefix == 'ix':
                context_dict = self._clean_context(elt)  # todo handle the full header as a data element only. Save the references somewhere.
            elif elt.name == "table":
                table_content, local_structured_data = self._clean_table(elt, context_dict)
                string_elts.append(table_content)
                structured_data.extend(local_structured_data)
            elif elt.name == 'a':
                string_elts.append(elt.get_text())
            elif elt.name == 'span' and ('font-size:5.85pt;' in elt.attrs.get('style', '')):
                if any(elt.children):
                    for c in elt.children:
                        stack.append(c)
                else:
                    string_elts.append(elt.get_text())
            # TODO - these are footnotes. Consider rewriting to "see footnote [n] for increasing n."
            # but doc reuses numbers.
            # if you do it, you can find footnotes as ix:footnote id="fn-1"
            # track most recent version of the number. then when you see an ix:footnote, swap the number
            # to here.
            # full footnote:
                """
                <div>
                    <span style="color:#000000;font-family:'Arial Narrow',sans-serif;font-size:5.2pt;font-weight:400;line-height:120%;position:relative;top:-2.8pt;vertical-align:baseline">
                        1
                    </span>
                    <span style="color:#000000;font-family:'Arial Narrow',sans-serif;font-size:8pt;font-weight:400;line-height:120%">
                        <ix:footnote id="fn-1" footnoteRole="http://www.xbrl.org/2003/role/footnote">Non-cash amounts are included in Canada wind-down costs on the Condensed Consolidated Statement of Cash Flows.</ix:footnote>
                    </span>
                </div>
                """
            else:
                if any(elt.children):
                    stack.extend(reversed(list(elt.children)))
                else:
                    string_elts.append(elt.get_text())
        
        return ParserReturn(
                   parsed_doc=[s for s in string_elts if s and 'amounts in millions' not in s.lower()],
                   structured_data=structured_data
        )

    def _clean_context(self, elt : BeautifulSoup) -> Dict[str, any]:
        ret_dict = {}

        resources = elt.find_next(lambda x: x.name == 'resources' and x.prefix == 'ix')
        for child in resources.children:
            if child.name == 'context':
                child_id = child.attrs['id']
                
                # try to parse a period
                periods = child.find_all('period')
                if len(periods) != 1:
                    raise NotImplementedError(f"Resource {child}")
                period : BeautifulSoup = periods[0]
                value_dict = {}
                for period_elt in period.children:
                    if period_elt.name is not None:
                        value_dict[period_elt.name] = period_elt.get_text()

                ret_dict[child_id] = value_dict    
            elif child.name == 'unit':
                # TODO: also parse units.
                pass
        
        return ret_dict

    def _clean_table(self, table : BeautifulSoup, context_table: Dict[str, any]) -> (str, Dict[str, any]):
        if len(table.find_all(lambda x: x.prefix == 'ix')) > 0:
            return self._clean_structured_table(table, context_table)
        else:
            return self._clean_simple_table(table), []

    def _clean_simple_table(self, table : BeautifulSoup) -> str:
        stack = [table]
        while len(stack):
            elt = stack.pop()
            if elt.name == 'span' or elt.name == 'div' or elt.name is None:
                elt.replace_with(elt.get_text())
            else:
                stack.extend(reversed(list(elt.children)))

        # remove style from all elements in the table.
        table.attrs = {}
        for elt in table.find_all():
            elt.attrs = {}

        return str(table)

    def _clean_structured_table(self, table : BeautifulSoup, context_table: Dict[str, any]) -> (str, Dict[str, any]):
        # remove style from all elements in the table.
        # todo drop (Amounts in millions except per share amounts)
        data_elts = []
        stack = [table]

        while len(stack):
            elt = stack.pop()
            if elt.name is None:
                pass
            elif elt.name == 'table':
                stack.extend(reversed(list(elt.children)))
            elif elt.name == 'tr':
                ix_elts = elt.find_all(lambda z: z.prefix == 'ix')
                if len(ix_elts) > 0:
                    # case 1: use parser
                    data_elts.extend(self._parse_structured_tr(elt, context_table))
                else:
                    pass
            else:
                raise ValueError(f"Unexpected elt in structured table parser: {elt}")
                    
        # make a table from data_elts.
        md_table = self._make_markdown(data_elts)
        return md_table, data_elts
    
    def _parse_structured_tr(self, tr : BeautifulSoup, context_table: Dict[str, any]):
        """Assume we have a tr element. Parse out possible key (first non-ix containing) and all values."""
        current_label = ''
        structured_data_elements = []
        
        for td in tr.children:  # assuming well-formatted here. could verify all children are td.
            if td.name is None:
                continue

            ix_elts = td.find_all(lambda z: z.prefix == 'ix')
            if len(ix_elts) >= 1:
                for ix_elt in ix_elts:
                    structured_data = self._get_single_ix_elt(ix_elt)
                    structured_data.update(context_table[structured_data['contextRef']])
                    structured_data_elements.append(structured_data)
            else:
                candidate_label = td.get_text()
                current_label = candidate_label if len(candidate_label) > len(current_label) else current_label

        # apply_label to each row.
        for elt in structured_data_elements:
            elt['rowLabel'] = current_label

        return structured_data_elements

    def _get_single_ix_elt(self, elt : BeautifulSoup):
        """Clean and return structured data"""
        vals = {
            'eltName': elt.name,
            'contextRef': elt.attrs.get('contextRef'),
            'ixName': elt.attrs.get('name'),
            'scale': float(elt.attrs.get('scale', 1)),
            'decimals': elt.attrs.get('decimals', 0),
            'factId': elt.attrs.get('id'),
            'unit': elt.attrs.get('unitRef'),
            'format': elt.attrs.get('format')
        }
        vals['raw_value'] = elt.get_text()

        try:
            raw_value = float(elt.get_text().replace(',', ''))
        except ValueError:
            vals['value'] = vals['raw_value']
        else:
            vals['value'] = (10**vals['scale']) * raw_value
        return vals

    def _make_markdown(self, row_list):

        """
        Thanks, GPT!

        Return a string containing a markdown-formatted table. The table is generated from the supplied list of dicts that
        contain row data, and a list of column names which refer to keys in the dicts. Column widths are automatically
        calculated. The optional fill_empty argument defines the value inserted into cells that don't have data.
        """

        keys_to_keep = {
            'rowLabel': "Label", 
            'value': "Value", 
            #'ixName': "InternalLabel",
            'id': "fact id",
            'format': "datatype",
            'startDate': "Period Start",
            'endDate': "Period End",
            'instant': ""}
        row_list = [{k: v for k, v in r.items() if k in keys_to_keep.keys()} for r in row_list]
        for row in row_list:
            if 'instant' in row:
                row['endDate'] = row['instant']
        del keys_to_keep['instant']

        for row in row_list:
            for k in keys_to_keep.keys():
                if not row.get(k):
                    row[k] = ""

        # Calculate the width of each column. This is derived from the max length of the row contents in a column including
        # the column name itself.
        col_widths = {
            col_name: max([len(str(r[col_name])) for r in row_list] + [len(col_name)]) for col_name in keys_to_keep
        }

        # Generate a format string that can later be used to print the rows of the table. In the above example this would
        # work out to: "{animal:<6} | {color:<5} | {feature:<12}"
        row_fmt = ' | '.join([
            f' {{{{{{name}}:<{{width}}}}}}'.format(name=col_name, width=col_widths[col_name])
            for col_name in keys_to_keep.keys()
        ])

        # The header row contains just the names of the columns.

        # The delimiter row contains the dash/underlines that appear on the line below the header row (this is vital for md
        # tables to be parsed as tables).
        delim_row = {col_name: "-" * col_widths[col_name] for col_name in keys_to_keep.keys()}
        
        try:
            return "\n".join([row_fmt.format(**row) for row in [keys_to_keep, delim_row] + row_list])
        except:
            import pdb; pdb.set_trace()
            a = 1 
