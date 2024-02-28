import json
from django.db import models
import markdown

from .rfpstuff.known_fact_formatters import (
    format_specific_date_to_object,
    format_requirements,
)

from privateuploads.models import DocumentCluster, DocumentExtract
from webserve.mixins import ModelBaseMixin


ModelOutputRoles = [  # if you modify this, also modify KnownFactExtractor!
    ("longsummary", "longsummary"),
    ("shortsummary", "shortsummary"),
    ("req_details", "req_details"),
    ("specific_dates", "specific_dates"),
    ("legal_notes", "legal_notes"),
    ("certifications", "certifications"),
    ("expertise", "expertise"),
    ("vendors", "vendors"),
    ("suggested_questions", "suggested_questions"),
    ("peoplesummary", "peoplesummary"),
    ("proposalquestions", "proposalquestions"),
    ("tocextract", "tocextract"),
]


class PromptResponse(ModelBaseMixin):
    """
    This is only used in structured document problems like RFPs. DO NOT use for consumer project.
    """

    template_name = models.CharField(max_length=64)
    template_version = models.SmallIntegerField()

    # this is the meaning of an output if there is a specific meaning. Example is extracting dates.
    output_role = models.CharField(max_length=64, choices=ModelOutputRoles)

    result = models.TextField()
    document_inputs = models.ManyToManyField(DocumentExtract)

    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)

    model_service = models.TextField()
    model_name = models.TextField()

    def as_html(self):
        return markdown.markdown(self.result, extensions=["extra"])


class ExtractedFact(ModelBaseMixin):
    # Assume this is JSON
    fact_contents = models.TextField()
    output_role = models.CharField(max_length=64, choices=ModelOutputRoles)

    doc_context = models.ForeignKey(DocumentCluster, on_delete=models.CASCADE)

    """sort_order is within output_role."""
    sort_order = models.IntegerField(default=0)

    def as_html(self):
        content = json.loads(self.fact_contents)
        if "text" in content:
            return markdown.markdown(content["text"], extensions=["extra"])

        return markdown.markdown(
            f"```\n{json.dumps(self.fact_contents, indent=4)}\n```"
        )

    def as_object(self):
        if self.output_role == "specific_dates":
            return format_specific_date_to_object(self.fact_contents)
        elif self.output_role in ("req_details", "certifications"):
            return format_requirements(self.fact_contents)
        else:
            return self.as_html()
