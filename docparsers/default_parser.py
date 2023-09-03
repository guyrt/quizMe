from bs4 import BeautifulSoup
from typing import List

class DefaultParser:

    def parse(self, dom : BeautifulSoup) -> List[str]:
        return dom.get_text().split("\n")
        