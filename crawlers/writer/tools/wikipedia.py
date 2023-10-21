import wikipedia

from .base import Tool
from ..writer_types import KnownFact, KnownFactInternal, KnownFactSource

from typing import Optional, List

wikipedia.set_lang('en')
WIKIPEDIA_MAX_QUERY_LENGTH = 300


class Wikipedia(Tool):

    name = "wikipedia"
    description = (
        "A wrapper around Wikipedia. Useful when you need to gather general background "
        "about people, places, companies, industries, or historical events. "
        "Input should the name of the wikipedia page you want to find."
    )

    def __init__(self) -> None:
        self.doc_content_chars_max: int = 4000
        self.top_k_results : int = 3
        self.load_all_available_meta: bool = False

    def run(self, query : str) -> List[KnownFact]:
        page_titles = wikipedia.search(query[:WIKIPEDIA_MAX_QUERY_LENGTH])

        summaries = []
        for page_title in page_titles[: self.top_k_results]:
            if wiki_page := self._fetch_page(page_title):
                summary = self._page_to_document(query, wiki_page)
                summaries.append(summary)

                if page_title.lower() == query.lower():
                    break

        if not summaries:
            print(f"No good Wikipedia Search Result was found for {query}")

        return summaries
    
    def _fetch_page(self, page: str) -> Optional[str]:
        try:
            return wikipedia.page(title=page, auto_suggest=False)
        except (
            wikipedia.exceptions.PageError,
            wikipedia.exceptions.DisambiguationError,
        ):
            return None
        
    def _page_to_document(self, query: str, wiki_page : wikipedia.wikipedia.WikipediaPage) -> KnownFact:
        return KnownFact(
            value=wiki_page.summary,
            long_value=wiki_page.content[:self.doc_content_chars_max],
            source=KnownFactSource(
                source_type=self.name,
                value=wiki_page.url
            ),
            internal=KnownFactInternal(
                query=query
            )
        )
