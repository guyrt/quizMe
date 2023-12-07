from django.db import models
from users.models import User

from extensionapis.models import SingleUrl

from webserve.mixins import ModelBaseMixin


# Create your models here.
class SimpleQuiz(ModelBaseMixin):
    """Starter model - just stores a JSON blob."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=10000)
