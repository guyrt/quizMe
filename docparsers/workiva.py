from bs4 import BeautifulSoup
from typing import List, Dict
import json


class WorkivaParser:

    def parse(self, dom : BeautifulSoup) -> List[str]:
        string_elts = []
        
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
                table_content = self._clean_table(elt, context_dict)
                string_elts.append(table_content)
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
        
        return [s for s in string_elts if s and 'amounts in millions' not in s.lower()]

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

    def _clean_table(self, table : BeautifulSoup, context_table: Dict[str, any]) -> str:
        if len(table.find_all(lambda x: x.prefix == 'ix')) > 0:
            return self._clean_structured_table(table, context_table)
        else:
            return self._clean_simple_table(table)

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

    def _clean_structured_table(self, table : BeautifulSoup, context_table: Dict[str, any]) -> str:
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
        return json.dumps(data_elts)
    
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
            'id': elt.attrs.get('id'),
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
