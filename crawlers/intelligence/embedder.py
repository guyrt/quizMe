from sentence_transformers import SentenceTransformer


class Embedder:

    def __init__(self) -> None:
        self._model = SentenceTransformer('BAAI/bge-large-en-v1.5')

    def embed(self, content):
        return self._model.encode(content, normalize_embeddings=True)

    def embed_query(self, content):
        q = 'Represent this sentence for searching relevant passages: '
        self._model.encode(q + content, normalize_embeddings=True)

