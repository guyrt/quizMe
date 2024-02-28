from sentence_transformers import SentenceTransformer


from django.conf import settings


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class WebDocEmbedder:
    """Basic embedder - only one kind for now."""

    def __init__(self, embedding_name=None) -> None:
        if embedding_name is None:
            embedding_name = settings.DEFAULT_WEB_EMBEDDING_MODEL
        self.embedding_name = embedding_name
        self._model = SentenceTransformer(self.embedding_name)

    def embed(self, content):
        return self._model.encode(content, normalize_embeddings=True, batch_size=16)

    def embed_query(self, content):
        q = "Represent this sentence for searching relevant passages: "
        self._model.encode(q + content, normalize_embeddings=True)
