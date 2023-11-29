from django.db import models

from users.models import User


# Create your models here.
class AuthTokens(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    key = models.CharField(max_length=128)

    name = models.CharField(max_length=64)
