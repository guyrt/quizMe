from typing import List
from uuid import UUID
from bs4 import BeautifulSoup
from django.db import transaction
from django_rq import job

from extensionapis.models import RawDocCapture, SingleUrl, SingleUrlFact
from mltrack.consumer_prompt_models import UserLevelVectorIndex
from ..utilities import parse_contents

from .recursive_html_chunker import RecursiveHtmlChunker
from .web_embedder import WebDocEmbedder

import logging

logger = logging.getLogger("default")


class WebParserDriver:
    """Main parser driver for our web content"""

    def __init__(self) -> None:
        self._embedder = WebDocEmbedder()

    def process_impression(self, impression : RawDocCapture):
        # you could group these two statements in async.
        raw_dom = parse_contents(impression.get_content_prefer_readable())
        single_url = impression.url_model

        # these can run in parallel
        #self._classify_article(single_url, raw_dom)
        self._index_text(impression, raw_dom)

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

    def _index_text(self, impression : RawDocCapture, raw_dom : BeautifulSoup):
        chunks = RecursiveHtmlChunker().parse(raw_dom)
        logger.info("Parsed raw doc %s into %s chunks", impression.pk, len(chunks))

        embeddings = self._embedder.embed([chunk.content for chunk in chunks])
        vector_models : List[UserLevelVectorIndex] = []
        for i, chunk in enumerate(chunks):
            embedding = embeddings[i]

            vector_models.append(
                UserLevelVectorIndex(
                    user=impression.user,
                    doc_id=impression.guid,
                    doc_url=impression.url,

                    doc_chunk=chunk.content,
                    doc_chunk_type=chunk.reason,
                    embedding=embedding.tolist(),
                    embedding_type=self._embedder.embedding_name
                )
            )

        self._update_for_doc(impression.pk, vector_models)

    def _update_for_doc(self, doc_guid : UUID, new_vectors : List[UserLevelVectorIndex]):
        with transaction.atomic():
            UserLevelVectorIndex.objects.filter(doc_id=doc_guid).delete()
            UserLevelVectorIndex.objects.bulk_create(new_vectors)


@job
def process_raw_doc(pk : str):
    logger.info("Start to process %s", pk)
    w = WebParserDriver()
    r = RawDocCapture.objects.get(guid=pk)
    w.process_impression(r)
