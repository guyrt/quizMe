from django.db import models

from users.models import User

from webserve.mixins import ModelBaseMixin

# Create your models here.
class AuthTokens(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    key = models.CharField(max_length=128)

    name = models.CharField(max_length=64)


class RawDocCapture(ModelBaseMixin):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    location_container = models.CharField(max_length=64)
    location_path = models.CharField(max_length=256)


class ParsedDocCapture(ModelBaseMixin):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    raw_doc = models.ForeignKey(RawDocCapture, on_delete=models.CASCADE)

    # Todo more stuff