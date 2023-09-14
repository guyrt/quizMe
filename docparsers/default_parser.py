from bs4 import BeautifulSoup
from typing import List

from .docparsertypes import ParserReturn

class DefaultParser:

    def parse(self, dom : BeautifulSoup) -> ParserReturn:
        return ParserReturn(dom.get_text().split("\n"), [])
        