from bs4 import BeautifulSoup
from typing import List
import json

class WorkivaParser:

    def parse(self, dom : BeautifulSoup) -> List[str]:
        string_elts = []
        
        stack = [dom]

        while len(stack):
            elt = stack.pop()

            if elt.name is None:
                s = elt.get_text().strip()
                if s:
                    string_elts.append(s)
                continue

            if elt.name == 'header' and elt.prefix == 'ix':
                pass  # todo handle the full header as a data element only. Save the references somewhere.
            elif elt.name == "table":
                table_content = self._clean_table(elt)
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
        
        return [s for s in string_elts if s]

    def _clean_table(self, table : BeautifulSoup) -> str:
        if len(table.find_all('ix:nonFraction')) > 0:
            return self._clean_structured_table(table)
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

    def _clean_structured_table(self, table : BeautifulSoup) -> str:
        # remove style from all elements in the table.
        # todo drop (Amounts in millions except per share amounts)
        data_elts = []
        stack = [table]
        while len(stack):
            elt = stack.pop()
            if elt.name == 'table':
                stack.extend(reversed(list(elt.children)))
            if elt.name == 'tr':
                # two cases:
                    # something has an ix. parse entire row as that, keeping the initial non-empty col as a key.
                    # nothing does. ignore.
                stack.extend(reversed(list(elt.children)))
            elif elt.name == 'td':
                ix_elts = elt.find_all(lambda z: z.prefix == 'ix')
                if len(ix_elts) == 1:
                    structured_data = self._get_single_ix_elt(elt)
                    import ipdb; ipdb.set_trace()
                elif len(ix_elts) > 1:
                    raise ValueError(f"too many ix elts in a td: {elt}")
                else:
                    elt.attrs = {}
                    
                # if you have an ix namespace child just use it.
                # if not then use get_text

        # make a table
        return data_elts
    
    def _get_single_ix_elt(self, elt):
        """Clean and return structured data"""
        import ipdb; ipdb.set_trace()



