import wikipedia

from .base import Tool

from typing import Optional

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

    def run(self, query):
        # TODO: must return KnownFacts (or KnownSources or something?).
        page_titles = wikipedia.search(query[:WIKIPEDIA_MAX_QUERY_LENGTH])

        summaries = []
        for page_title in page_titles[: self.top_k_results]:
            if wiki_page := self._fetch_page(page_title):
                if summary := self._page_to_document(page_title, wiki_page):
                    summaries.append(summary)
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
        
    def _page_to_document(self, page_title: str, wiki_page):
        main_meta = {
            "title": page_title,
            "summary": wiki_page.summary,
            "source": wiki_page.url,
        }
        add_meta = (
            {
                "categories": wiki_page.categories,
                "page_url": wiki_page.url,
                "image_urls": wiki_page.images,
                "related_titles": wiki_page.links,
                "parent_id": wiki_page.parent_id,
                "references": wiki_page.references,
                "revision_id": wiki_page.revision_id,
                "sections": wiki_page.sections,
            }
            if self.load_all_available_meta
            else {}
        )
        doc = {
            'page_content': wiki_page.content[: self.doc_content_chars_max],
            'metadata': {
                **main_meta,
                **add_meta,
            },
        }
        return doc