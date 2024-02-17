from extensionapis.models import RawDocCapture
from mltrack.consumer_prompt_models import UserLevelVectorIndex


class NoChunksError(Exception):
    pass


def find_relevant_chunks(raw_doc : RawDocCapture):
    """
    get chunks for the doc
    filter to non-headers
    for each chunk get high matches
    for each chunk return top 3
    """

    chunks = list(UserLevelVectorIndex.objects.filter(
        doc_id=raw_doc.guid
    ).exclude(doc_chunk_type='header'))

    if len(chunks) == 0:
        raise NoChunksError()

    chunk_matches = []
    for chunk in chunks:
        matches = UserLevelVectorIndex.objects.search_by_embedding(
            user_id=raw_doc.user.pk,
            embedding_vector=chunk.embedding,
            excluding_doc_id=raw_doc.guid,
            take=3
        )

        processed_matches = [
            {
                'doc_id': m.doc_id,
                'url': m.doc_url,
                'chunk': m.chunk,
                'rank': i
            }
        for i, m in enumerate(matches)]

        chunk_matches.append({
            'chunk': chunk.doc_chunk,
            'matches': processed_matches
        })

    # todo make this an object.
    return chunk_matches
