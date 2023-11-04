from django.db import models
import json
import markdown
from users.models import User
from webserve.mixins import ModelBaseMixin

from typing import Literal, Tuple, List

from privateuploads.types import DocFormat

from azurewrapper.rfp.extractedtext_handler import KMExtractedTextBlobHander


ProjectTypes = Literal['RFP', 'PublicSEC']



DocChoices : List[Tuple[DocFormat, DocFormat]]= [
    ("pdf", "pdf"),
    ("docx", "docx"),
    ('zip', 'zip')
]


ProcessingChoices = [
    ("notstarted", "notstarted"),
    ("done", "done"),
    ("active", "active"),
    ("error", "error")
]


FileRoles = Literal['rfp', 'unknown']


# todo - this only applies to RFP docs right now.
DocumentClusterRoleChoices = [
    ('rfp', 'RFP'),
    ('proposal', 'Proposal'),
    ('resume', 'Resume'),
    ('verbatim', 'Verbatim Templates'),
    ('intelligence', 'Customer Intelligence'),
    ('unknown', 'None')
]


FileRolesChoices = [
    ('primary', 'Primary'),
    ('unknown', 'None')
]


class DocumentCluster(ModelBaseMixin):
    """A document cluster is a set of related docs. Example would be a single SEC filing
    or single RFP. These may have many underlying documents.
    """

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # Role within RFP project. 
    document_role = models.CharField(max_length=16, choices=DocumentClusterRoleChoices)

    def get_title(self):
        return self.documentfile_set.get(active=True).doc_name


class RawUpload(ModelBaseMixin):

    document = models.ForeignKey(DocumentCluster, on_delete=models.CASCADE)
    format = models.CharField(max_length=8, choices=DocChoices)
    
    location_container = models.CharField(max_length=64)
    location_path = models.CharField(max_length=256)


class DocumentFile(ModelBaseMixin):

    document = models.ForeignKey(DocumentCluster, on_delete=models.CASCADE)
    source = models.ForeignKey(RawUpload, on_delete=models.CASCADE)

    file_role = models.CharField(max_length=16, choices=FileRolesChoices)  # TODO track main file vs addendum ect.
    doc_format = models.CharField(max_length=8, choices=DocChoices)
    doc_name = models.TextField()  # name of doc as a relative path to root.

    location_container = models.CharField(max_length=64)
    location_path = models.CharField(max_length=256)

    # Tell us current process state.
    processing_status = models.CharField(max_length=16, choices=ProcessingChoices)
    last_jobid = models.CharField(max_length=32, default='')


class DocumentExtract(ModelBaseMixin):

    docfile = models.ForeignKey(DocumentFile, on_delete=models.CASCADE)

    location_container = models.CharField(max_length=64)
    location_path = models.CharField(max_length=256)

    def get_content(self) -> str:
        return KMExtractedTextBlobHander(self.location_container).get_path(self.location_path)
        
    def get_clean_content(self):
        raw_content = json.loads(self.get_content())
        return raw_content['content']

    def as_html(self):
        c = json.loads(self.get_content())
        if c['format'] == 'html':
            return c['content']
        return markdown.markdown(''.join(c['content']), extensions=['extra'])
