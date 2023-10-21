from django.db import models
from users.models import User
from webserve.mixins import ModelBaseMixin

from typing import Literal, Tuple, List


UploadSources = Literal['RFP', 'PublicSEC']


DocFormats = [
    ("pdf", "pdf"),
    ("docx", "docx"),
    ('zip', 'zip')
]


ProcessingChoices = [
    ("done", "done"),
    ("active", "active"),
    ("error", "error")
]


class DocumentCluster(ModelBaseMixin):
    """A document cluster is a set of related docs. Example would be a single SEC filing
    or single RFP. These may have many underlying documents.
    """

    UploadSourceChoices : List[Tuple[UploadSources, UploadSources]] = [
        ("RFP", "RFP"),
        ("PublicSEC", "PublicSEC")
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    upload_source = models.CharField(max_length=16, choices=UploadSourceChoices)


class RawUpload(ModelBaseMixin):

    document = models.ForeignKey(DocumentCluster, on_delete=models.CASCADE)
    format = models.CharField(max_length=8, choices=DocFormats)
    
    location_container = models.CharField(max_length=64)
    location_path = models.CharField(max_length=256)


class DocumentFile(ModelBaseMixin):

    document = models.ForeignKey(DocumentCluster, on_delete=models.CASCADE)
    source = models.ForeignKey(RawUpload, on_delete=models.CASCADE)

    file_role = models.CharField(max_length=16)  # TODO track main file vs addendum ect.
    doc_format = models.CharField(max_length=8, choices=DocFormats)
    doc_name = models.TextField()  # name of doc as a relative path to root.

    location_container = models.CharField(max_length=64)
    location_path = models.CharField(max_length=256)

    # Tell us current process state.
    processing_status = models.CharField(max_length=8, choices=ProcessingChoices)
    last_jobid = models.CharField(max_length=32)


class DocumentExtract(ModelBaseMixin):

    docfile = models.ForeignKey(DocumentFile, on_delete=models.CASCADE)

    location_container = models.CharField(max_length=64)
    location_path = models.CharField(max_length=256)

