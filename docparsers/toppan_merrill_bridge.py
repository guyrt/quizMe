from bs4 import BeautifulSoup

class ToppanMerrillBridgeParser:

    def parse(self, dom : BeautifulSoup) -> str:
        string_elts = []
        text_elts = dom.find_all(['a', 'p'])
        for elt in text_elts:
            if elt.string:
                string_elts.append(elt.string)
        
        return "\n".join(string_elts)