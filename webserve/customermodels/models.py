from django.db import models
from users.models import User
from webserve.mixins import ModelBaseMixin

# TODO: we want relationships to be stored in the structured layer.


#
# Structure tables
#
class UserTable(ModelBaseMixin):
    """Stores a table shape reference"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=4096)


class UserTableColumn(ModelBaseMixin):
    """Stores a single table shape column reference."""

    table = models.ForeignKey(UserTable, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=4096)
    dtype = models.CharField(max_length=64, blank=True, default="")


#
# Data tables
#
class RawUserTableEntry(ModelBaseMixin):
    """Immutable entry extracted from some source document."""

    table = models.ForeignKey(UserTable, on_delete=models.CASCADE)
    content = models.JSONField(default=dict)

    # source info
    source_table = models.CharField(max_length=128)
    source_pk = models.UUIDField()


class UserTableEntry(ModelBaseMixin):
    table = models.ForeignKey(UserTable, on_delete=models.CASCADE)
    content = models.JSONField(default=dict)

    raw_entries = models.ManyToManyField(to=RawUserTableEntry)
