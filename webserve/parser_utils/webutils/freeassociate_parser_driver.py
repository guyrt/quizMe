from typing import List
from uuid import UUID
from bs4 import BeautifulSoup
from django.db import transaction
from django_rq import job
from torch import sin

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
        self._index_text(impression, single_url, raw_dom)

    def _extract_and_create_links(self, raw_dom : BeautifulSoup):
        pass

    def _index_text(self, impression : RawDocCapture, single_url : SingleUrl, raw_dom : BeautifulSoup):
        chunks = RecursiveHtmlChunker().parse(raw_dom)
        chunks = [c for c in chunks if len(c) > 0]
        logger.info("Parsed raw doc %s into %s chunks", impression.pk, len(chunks))

        embeddings = self._embedder.embed([chunk.content for chunk in chunks])
        vector_models : List[UserLevelVectorIndex] = []
        for i, chunk in enumerate(chunks):
            embedding = embeddings[i]

            vector_models.append(
                UserLevelVectorIndex(
                    user=impression.user,
                    doc_id=single_url.pk,
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
def process_raw_doc(single_url_pk : int):
    logger.info("Start to process %s", single_url_pk)
    w = WebParserDriver()
    surl = SingleUrl.objects.get(id=single_url_pk)
    r = surl.rawdoccapture_set.order_by('-date_added').first()

    w.process_impression(r)
