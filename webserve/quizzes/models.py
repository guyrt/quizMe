import uuid

from django.db import models
from users.models import User

from extensionapis.models import SingleUrl

from webserve.mixins import ModelBaseMixin


class SimpleQuiz(ModelBaseMixin):
    """Starter model - just stores a JSON blob."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=10000)
    reasoning = models.TextField(max_length=10000)  # the natural language reasoning.

    url = models.ForeignKey(SingleUrl, on_delete=models.CASCADE)
