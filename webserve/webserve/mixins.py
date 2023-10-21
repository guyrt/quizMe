from django.db import models


class ModelBaseMixin(models.Model):
    """
    Please include this or a subclass on ALL internally defined models. It provides
    us with tracking criteria.
    """

    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
