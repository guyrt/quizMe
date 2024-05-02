from django.db import models
from users.models import User
from webserve.mixins import ModelBaseMixin

# TODO: we want relationships to be stored in the structured layer.


#
# Structure tables
#
class UserSchema(ModelBaseMixin):
    """Stores a reference to set of tables"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=4096)


class UserTable(ModelBaseMixin):
    """Stores a table shape reference"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    schema = models.ForeignKey(UserSchema, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=4096)


class UserTableColumn(ModelBaseMixin):
    """Stores a single table shape column reference."""

    table = models.ForeignKey(UserTable, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=4096)
    dtype = models.CharField(max_length=64, blank=True, default="")


class ExtractionStatusChoices(models.TextChoices):
    InProgress = "inprogress", "inprogress"
    Done = "done", "done"
    Error = "error", "error"


#
# Data tables
#
class RawDocumentExtract(ModelBaseMixin):

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    source_table = models.CharField(max_length=64)
    source_pk = models.UUIDField()

    extraction_target = models.CharField(max_length=64)  # table name of a model that contains extraction target
    extraction_pk = models.UUIDField()

    extracted_content = models.JSONField()

    extraction_status = models.CharField(choices=ExtractionStatusChoices)

    extraction_model_details = models.JSONField()
