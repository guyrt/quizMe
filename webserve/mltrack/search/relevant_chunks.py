from enum import Enum
from django.db import models
from extensionapis.models import SingleUrl
from mltrack.consumer_prompt_models import UserLevelDocVectorIndex, UserLevelVectorIndex


class NoChunksError(Exception):
    pass


def find_relevant_chunks(url_obj: SingleUrl):
    """
    get chunks for the doc
    filter to non-headers
    for each chunk get high matches
    for each chunk return top 3
    """

    chunks = list(
        UserLevelVectorIndex.objects.filter(doc_id=url_obj.pk).exclude(
            doc_chunk_type="header"
        )
    )

    if len(chunks) == 0:
        raise NoChunksError()

    chunk_matches = []
    for chunk in chunks:
        matches: models.Manager = UserLevelVectorIndex.objects.search_by_embedding(
            user_id=url_obj.user.pk,
            embedding_vector=chunk.embedding,
            exclude_doc_id=url_obj.pk,
            take=3,
            include_dist=True,
        )

        processed_matches = [
            {
                "doc_id": m.doc_id,
                "url": m.doc_url,
                "chunk": m.doc_chunk,
                "rank": i,
                "score": m.dist,
            }
            for i, m in enumerate(matches)
        ]

        chunk_matches.append({"chunk": chunk.doc_chunk, "matches": processed_matches})

    # todo make this an object.
    return chunk_matches


class RelevantDocumentIndexChoice(str, Enum):
    maxChunkMatch = "maxchunk"
    sifOnChunkAverage = "SifFromChunkAverage"


def find_relevant_docs(url_obj: SingleUrl, strategy: RelevantDocumentIndexChoice):
    if strategy is None:
        strategy = RelevantDocumentIndexChoice.maxChunkMatch

    if strategy == RelevantDocumentIndexChoice.maxChunkMatch:
        return _find_relevant_docs_max_chunk(url_obj)
    elif strategy == RelevantDocumentIndexChoice.sifOnChunkAverage:
        return _find_relevant_docs_sif(url_obj)
    else:
        raise ValueError(f"Unexpected value {strategy}")


def _find_relevant_docs_sif(raw_doc: SingleUrl):
    try:
        docs = UserLevelDocVectorIndex.objects.filter(doc_id=raw_doc.pk).get()
    except UserLevelDocVectorIndex.DoesNotExist:
        raise NoChunksError()

    doc_results = UserLevelVectorIndex.objects.search_by_embedding(
        user_id=raw_doc.user.pk,
        embedding_vector=docs.embedding,
        exclude_doc_id=raw_doc.pk,
        take=5,
        include_dist=True,
    )

    return [
        {"doc_id": str(doc.pk), "doc_url": doc.doc_url, "score": doc.dist}
        for doc in doc_results
    ]


_threshold = 0.5


def _find_relevant_docs_max_chunk(url_obj: SingleUrl):
    """Simple strategy... take max score"""
    chunks = list(
        UserLevelVectorIndex.objects.filter(doc_id=url_obj.pk).exclude(
            doc_chunk_type="header"
        )
    )

    if len(chunks) == 0:
        raise NoChunksError()

    doc_matches = {}  # doc_id -> highest score
    doc_urls = {}  # doc_id -> url
    for chunk in chunks:
        matches: models.Manager = UserLevelVectorIndex.objects.search_by_embedding(
            user_id=url_obj.user.pk,
            embedding_vector=chunk.embedding,
            exclude_doc_id=url_obj.pk,
            take=3,
            include_dist=True,
        )

        for m in matches:
            doc_id = str(m.doc_id)
            if doc_id not in doc_matches:
                doc_matches[doc_id] = 1.0
                doc_urls[doc_id] = m.doc_url

            if doc_matches[doc_id] > m.dist:
                doc_matches[doc_id] = m.dist

    return [
        {"doc_id": k, "doc_url": doc_urls[k], "score": v}
        for k, v in doc_matches.items()
        if v < _threshold
    ]
