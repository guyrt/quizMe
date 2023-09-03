from bs4 import BeautifulSoup
from typing import List

class ToppanMerrillBridgeParser:

    def parse(self, dom : BeautifulSoup) -> List[str]:
        string_elts = []
        text_elts = dom.find_all(['a', 'p'])
        for elt in text_elts:
            if elt.string:
                string_elts.append(elt.string.strip())
        
        return [s for s in string_elts if s]
