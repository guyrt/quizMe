import bs4

from dataclasses import dataclass

from types import List

@dataclass
class Chunk:
    content : str
    reason : str


class RecursiveHtmlChunker:
    """Chunker that respects common HTML patterns.
    
    Aims for XXX length chunks.
    """

    def __init__(self) -> None:
        self._max_chunk_length = 1600  # 1600 characters
        self._min_chunk_length = 400 # min length we'll accept. Note that headers and other special elements may be shorter (but we may collapse them)
        pass

    def parse(self, dom : bs4.BeautifulSoup) -> List[Chunk]:
        """Enter the recursion then do post-process"""
        maybe_chunks = self._recurse(dom)

    def _recurse(self, dom : bs4.element.PageElement) -> List[Chunk | str]:
        if isinstance(dom, bs4.Comment):
            return []
        if isinstance(dom, bs4.NavigableString):
            return [dom.text]
        if isinstance(dom, bs4.Tag) and dom.name == 'a':
            # return text only.
            return [dom.text]
        if isinstance(dom, bs4.Tag) and dom.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return [Chunk(content=dom.text, reason='header')]
        if isinstance(dom, bs4.Tag) and dom.name in ['div', 'p']:
            # recurse!
            pass

