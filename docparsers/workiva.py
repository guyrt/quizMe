from bs4 import BeautifulSoup
from typing import List

class WorkivaParser:

    def parse(self, dom : BeautifulSoup) -> List[str]:
        string_elts = []
        
        stack = [dom]

        while len(stack):
            elt = stack.pop()
            if elt.name is None:
                string_elts.append(elt.get_text()) # eat for now... not sure if right but it's just a weird example for now.
            elif elt.name == "table":
                string_elts.append(self._clean_table(elt))
            elif elt.name == 'span' and ('font-size:5.85pt;' in elt.attrs.get('style')):
                pass
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
                    for c in elt.children:
                        stack.append(c)
                else:
                    string_elts.append(elt.get_text())
        
        return [s for s in string_elts if s]

    def _clean_table(self, table : BeautifulSoup) -> str:
        stack = [table]
        while len(stack):
            elt = stack.pop()
            if elt.name == 'span' or elt.name == 'div':
                elt.replace_with(elt.get_text())
            else:
                stack.extend(elt.children)

        # remove style from all elements in the table.
        table.attrs = {}
        for elt in table.find_all():
            elt.attrs = {}

        return str(table)
