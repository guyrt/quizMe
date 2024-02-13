from sentence_transformers import SentenceTransformer


from django.conf import settings

class WebDocEmbedder:
    """Basic embedder - only one kind for now."""

    def __init__(self, embedding_name=None) -> None:
        if embedding_name is None:
            embedding_name = settings.DEFAULT_WEB_EMBEDDING_MODEL
        self._embedding_name = embedding_name
        self._model = SentenceTransformer('BAAI/bge-large-en-v1.5')

    def embed(self, content):
        return self._model.encode(content, normalize_embeddings=True)

    def embed_query(self, content):
        q = 'Represent this sentence for searching relevant passages: '
        self._model.encode(q + content, normalize_embeddings=True)

# This will trigger a load of the model weights if one hasn't happened already. Cheap but we'll want to fix in prod.
default_web_embedder_singleton = WebDocEmbedder()
