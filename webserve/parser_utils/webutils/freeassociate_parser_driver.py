from bs4 import BeautifulSoup

from extensionapis.models import RawDocCapture, SingleUrl, SingleUrlFact
from ..utilities import parse_contents

from .recursive_html_chunker import RecursiveHtmlChunker
from .web_embedder import default_web_embedder_singleton

import logging

logger = logging.getLogger("default")


class WebParserDriver:
    """Main parser driver for our web content"""

    def __init__(self) -> None:
        self._embedder = default_web_embedder_singleton

    def process_impression(self, impression : RawDocCapture):
        # you could group these two statements in async.
        raw_dom = parse_contents(impression.get_content(True))
        single_url = impression.url_model

        # these can run in parallel
        #self._classify_article(single_url, raw_dom)
        self._index_text(impression.guid, raw_dom)

    def _extract_and_create_links(self, raw_dom : BeautifulSoup):
        pass

    def _classify_article(self, url_obj : SingleUrl, raw_dom : BeautifulSoup) -> SingleUrlFact:
        articles = raw_dom.find_all('article')
        if len(articles) > 0:
            # save this as an article.
            is_article = 'true'
        else:
            is_article = 'false'  # explicitly setting to false conveys that the url was once considered an article.
        
        # this is a pattern you could extract.
        obj, created = SingleUrlFact.objects.get_or_create(
            base_url=url_obj,
            fact_key="IsArticle",
            kwargs={
                'fact_value': "true"
            }
        )
        if created and obj.fact_value != is_article:
            obj.fact_value = is_article
            obj.save()

        return obj

    def _index_text(self, guid : str, raw_dom : BeautifulSoup):
        chunks = RecursiveHtmlChunker().parse(raw_dom)
        logger.info("Parsed raw doc %s into %s chunks", guid, len(chunks))

        for chunk in chunks:
            embedding = self._embedder.embed(chunk.content)
            print(embedding)
