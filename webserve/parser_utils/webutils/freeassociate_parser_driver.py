from typing import List
from bs4 import BeautifulSoup
from django.db import transaction
from django_rq import job
from pydantic import UUID4

from extensionapis.models import RawDocCapture, SingleUrl, SingleUrlFact
from mltrack.consumer_prompt_models import UserLevelVectorIndex, UserLevelDocVectorIndex
from parser_utils.webutils.doc_embedding import SifChunkToDocumentEmbeddingCreator
from users.models import User
from ..utilities import parse_contents

from .recursive_html_chunker import RecursiveHtmlChunker
from .web_embedder import WebDocEmbedder

import logging

logger = logging.getLogger("default")
# 224a6abd-0cd4-4491-88fe-0636ab037f2c


class WebParserDriver:
    """Main parser driver for our web content"""

    def __init__(self) -> None:
        self._embedder = WebDocEmbedder()

    def process_impression(self, impression: RawDocCapture):
        # you could group these two statements in async.
        try:
            raw_dom = parse_contents(impression.get_content_prefer_readable())
        except ValueError:
            logger.warning("Failed to find a blob for impression %s", impression.pk)

        single_url = impression.url_model

        try:
            article_class: SingleUrlFact = single_url.singleurlfact_set.get(
                fact_key="client_classification"
            )
            if article_class.fact_value != "article":
                return
        except SingleUrlFact.DoesNotExist:
            # not an article.
            return

        # these can run in parallel
        # self._classify_article(single_url, raw_dom)
        self._index_text(impression, single_url, raw_dom)

    def _extract_and_create_links(self, raw_dom: BeautifulSoup):
        pass

    def _index_text(
        self, impression: RawDocCapture, single_url: SingleUrl, raw_dom: BeautifulSoup
    ):
        chunks = RecursiveHtmlChunker().parse(raw_dom)
        chunks = [c for c in chunks if len(c) > 0]
        logger.info("Parsed raw doc %s into %s chunks", impression.pk, len(chunks))

        embeddings = self._embedder.embed([chunk.content for chunk in chunks])
        vector_models = self._create_chunk_embeddings(
            impression, single_url.pk, chunks, embeddings
        )

        doc_embedding = SifChunkToDocumentEmbeddingCreator().create_doc_embedding(
            embeddings
        )
        document_embedding_object = self._create_doc_embedding(
            single_url,
            impression.user,
            SifChunkToDocumentEmbeddingCreator.name(),
            doc_embedding,
        )
        self._update_for_doc(single_url, document_embedding_object, vector_models)

    def _create_chunk_embeddings(
        self, impression: RawDocCapture, single_url_pk: int, chunks, embeddings
    ):
        vector_models: List[UserLevelVectorIndex] = []
        for i, chunk in enumerate(chunks):
            embedding = embeddings[i]

            vector_models.append(
                UserLevelVectorIndex(
                    user=impression.user,
                    doc_id=single_url_pk,
                    doc_url=impression.url,
                    doc_chunk=chunk.content,
                    doc_chunk_type=chunk.reason,
                    embedding=embedding.tolist(),
                    embedding_type=self._embedder.embedding_name,
                    chunk_index=i,
                )
            )
        return vector_models

    def _create_doc_embedding(
        self, url: SingleUrl, user: User, embedding_strategy: str, doc_embedding
    ):
        return UserLevelDocVectorIndex(
            user=user,
            doc_id=url.pk,
            doc_url=url.url,
            embedding=doc_embedding.tolist(),
            embedding_type=self._embedder.embedding_name,
            vector_strategy=embedding_strategy,
        )

    def _update_for_doc(
        self,
        url: SingleUrl,
        doc_vector: UserLevelDocVectorIndex,
        new_vectors: List[UserLevelVectorIndex],
    ):
        with transaction.atomic():
            UserLevelDocVectorIndex.objects.filter(doc_id=url.pk).delete()
            UserLevelDocVectorIndex.objects.bulk_create([doc_vector])
            UserLevelVectorIndex.objects.filter(doc_id=url.pk).delete()
            UserLevelVectorIndex.objects.bulk_create(new_vectors)


@job
def process_raw_doc(single_url_pk: UUID4):
    logger.info("Start to process %s", single_url_pk)
    w = WebParserDriver()
    surl = SingleUrl.objects.get(id=single_url_pk)
    r = surl.rawdoccapture_set.order_by("-date_added").first()

    w.process_impression(r)
