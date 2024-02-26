from django.db import models
from users.models import User


class StripeUser(models.Model):

    id = models.CharField(primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)



class StripeErrorLog(models.Model):

    message = models.TextField()
    event_id = models.CharField(unique=True, max_length=128)
    triaged = models.BooleanField(default=False)
