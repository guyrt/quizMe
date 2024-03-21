from django.db import models
from extensionapis.models import RawDocCapture
from mltrack.consumer_prompt_models import UserLevelVectorIndex


class NoChunksError(Exception):
    pass


def find_relevant_chunks(raw_doc: RawDocCapture):
    """
    get chunks for the doc
    filter to non-headers
    for each chunk get high matches
    for each chunk return top 3
    """

    chunks = list(
        UserLevelVectorIndex.objects.filter(doc_id=raw_doc.pk).exclude(
            doc_chunk_type="header"
        )
    )

    if len(chunks) == 0:
        raise NoChunksError()

    chunk_matches = []
    for chunk in chunks:
        matches: models.Manager = UserLevelVectorIndex.objects.search_by_embedding(
            user_id=raw_doc.user.pk,
            embedding_vector=chunk.embedding,
            exclude_doc_id=raw_doc.pk,
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


def find_relevant_docs(raw_doc: RawDocCapture):
    """Simple strategy... take max score"""
    chunks = list(
        UserLevelVectorIndex.objects.filter(doc_id=raw_doc.pk).exclude(
            doc_chunk_type="header"
        )
    )

    if len(chunks) == 0:
        raise NoChunksError()

    doc_matches = {}  # doc_id -> highest score
    doc_urls = {}  # doc_id -> url
    for chunk in chunks:
        matches: models.Manager = UserLevelVectorIndex.objects.search_by_embedding(
            user_id=raw_doc.user.pk,
            embedding_vector=chunk.embedding,
            exclude_doc_id=raw_doc.pk,
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
    ]
