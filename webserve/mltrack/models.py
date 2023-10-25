from django.db import models
import markdown

from privateuploads.models import DocumentExtract
from webserve.mixins import ModelBaseMixin


ModelOutputRoles = [
    ('longsummary', 'longsummary'),
    ('shortsummary', 'shortsummary'),
    ('req_details', 'req_details'),
    ('specific_dates', 'specific_dates'),
    ('legal_notes', 'legal_notes'),
    ('certifications', 'certifications'),
    ('expertise', 'expertise'),
    ('vendors', 'vendors'),
    ('suggested_questions', 'suggested_questions')
]


# Create your models here.
class PromptResponse(ModelBaseMixin):

    template_name = models.CharField(max_length=64)
    template_version = models.SmallIntegerField()

    # this is the meaning of an output if there is a specific meaning. Example is extracting dates.
    output_role = models.CharField(max_length=64, choices=ModelOutputRoles)
    
    result = models.TextField()
    document_inputs = models.ManyToManyField(DocumentExtract)

    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)

    def as_html(self):
        return markdown.markdown(self.result, extensions=['extra'])
