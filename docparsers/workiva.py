from bs4 import BeautifulSoup
from typing import List

class WorkivaParser:

    def parse(self, dom : BeautifulSoup) -> List[str]:
        string_elts = []
        
        stack = []
        for child in dom.children:
            stack.append(child)

        while len(stack):
            elt = stack.pop()
            if elt.name is None:
                pass # eat for now... not sure if right but it's just a weird example for now.
            elif elt.name == "table":
                string_elts.append(self._clean_table(elt))
            else:
                if any(elt.children):
                    for c in elt.children:
                        stack.append(c)
                else:
                    string_elts.append(elt.get_text())
        
        return [s for s in string_elts if s]

    def _clean_table(self, table : BeautifulSoup) -> str:
        # remove style from all elements in the table.
        table.attrs = {}
        for elt in table.find_all():
            elt.attrs = {}

        # do a stack thing BUT...
        # if it's a span then replace with just text

        stack = [table]
        while len(stack):
            elt = stack.pop()
            if elt.name == 'span' or elt.name == 'div':
                elt.replace_with(elt.get_text())
            else:
                stack.extend(elt.children)

        return str(table)
