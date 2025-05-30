import uuid
from django.db import models
from .consumer_prompt_managers import UserLevelVectorIndexManager

from pgvector.django import VectorField

from users.models import User


class ConsumerPromptTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    template_name = models.CharField(max_length=64)
    template_version = models.SmallIntegerField()

    # todo -> document type, document id.
    source_type = models.CharField(
        max_length=64
    )  # name of the model you used to generate data
    source_id = models.CharField(
        max_length=48
    )  # pk of the model you used to generate data

    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)

    model_service = models.TextField()
    model_name = models.TextField()


class UserLevelVectorIndex(models.Model):
    """These store chunk level vectors."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_added = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # this should be a SingleUrl.
    doc_id = models.UUIDField()
    doc_url = models.CharField(max_length=2024)

    doc_chunk = models.TextField()
    doc_chunk_type = models.CharField(max_length=32)

    embedding = VectorField(dimensions=384)
    embedding_type = models.CharField(max_length=64)
    chunk_index = models.IntegerField()

    objects = UserLevelVectorIndexManager()


class UserLevelDocVectorIndex(models.Model):
    """These store page level vectors."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_added = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # this should be a SingleUrl.
    doc_id = models.UUIDField()
    doc_url = models.CharField(max_length=2024)

    embedding = VectorField(dimensions=384)

    # describe strategy to create doc embedding.
    # perhaps make a choice later.
    vector_strategy = models.CharField(max_length=64)

    embedding_type = models.CharField(max_length=64)

    objects = UserLevelVectorIndexManager()
