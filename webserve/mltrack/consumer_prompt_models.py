from django.db import models

from users.models import User

class ConsumerPromptTrack(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    template_name = models.CharField(max_length=64)
    template_version = models.SmallIntegerField()

    # todo -> document type, document id.
    source_type = models.CharField(max_length=64)  # name of the model you used to generate data
    source_id = models.CharField(max_length=16)  # pk of the model you used to generate data

    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)

    model_service = models.TextField()
    model_name = models.TextField()
