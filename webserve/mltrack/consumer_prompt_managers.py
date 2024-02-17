from django.db import models
from pgvector.django import L2Distance


class UserLevelVectorIndexManager(models.Manager):
    def search_by_embedding(self, user_id, embedding_vector, exclude_doc_id, take):
        """
        Search for vectors similar to 'embedding_vector' for a specific user,
        excluding a specific 'doc_id'.
        """

        # Create a query that always filters by the user and excludes the doc_id.
        query = self.filter(user_id=user_id).exclude(doc_id=exclude_doc_id)

        query.order_by(L2Distance('embedding', embedding_vector))[:take]
        
        return query
