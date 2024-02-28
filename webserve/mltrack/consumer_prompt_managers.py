from django.db import models
from pgvector.django import CosineDistance


class UserLevelVectorIndexManager(models.Manager):
    def search_by_embedding(
        self, user_id, embedding_vector, exclude_doc_id, take, include_dist=False
    ):
        """
        Search for vectors similar to 'embedding_vector' for a specific user,
        excluding a specific 'doc_id'.
        """

        # Create a query that always filters by the user and excludes the doc_id.
        query = self.filter(user_id=user_id).exclude(doc_id=exclude_doc_id)

        query = query.order_by(CosineDistance("embedding", embedding_vector))[:take]

        if include_dist:
            query = query.annotate(dist=CosineDistance("embedding", embedding_vector))

        return query
