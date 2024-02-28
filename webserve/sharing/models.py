from django.db import models

from users.models import User
from webserve.mixins import ModelBaseMixin


class ShareRequest(ModelBaseMixin):
    """Object to share specific types.

    Only supports paradigm of 'read only if you have the URL'
    """

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # expectation is that you store a type like 'module.models.MyType'
    shared_object = models.CharField(max_length=128)

    shared_pk = models.IntegerField()

    # GUID to redirect to.
    share_link = models.CharField(max_length=512)


class Feedback(ModelBaseMixin):
    share_link = models.CharField(max_length=512)  # soft FK to ShareRequest

    name = models.CharField(max_length=512)  # name of person giving feedback

    feedback = models.TextField(max_length=2048)
