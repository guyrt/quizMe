import numpy as np


class SifChunkToDocumentEmbeddingCreator:
    @staticmethod
    def name():
        return "SifFromChunkAverage"

    def create_doc_embedding(self, chunk_embeddings: np.ndarray) -> np.ndarray:
        means = chunk_embeddings.mean(axis=0)
        normalized_embeddings = chunk_embeddings - means
        U, s, V = np.linalg.svd(normalized_embeddings)
        principal_components = U @ np.diag(s)
        p1 = principal_components[0, :].reshape(-1, 1)
        final_embeddings = (
            normalized_embeddings - (normalized_embeddings.T @ (p1 @ p1.T)).T
        )
        return final_embeddings.mean(axis=0) + means
