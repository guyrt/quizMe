from django_rq import job

from privateuploads.models import DocumentFile

from .gpt_extract_rfp import RFPPromptRunner
from .gpt_extract_proposal import ProposalPromptRunner

from typing import List

import logging
logger = logging.getLogger(__name__)

@job
def gpt_extract(raw_docextracts : List[int], doc_file_id):
    doc_file = DocumentFile.objects.get(id=doc_file_id)
    doc_file.processing_status = 'active'
    doc_file.save()

    # get owner
    doc_role = doc_file.document.document_role
    if doc_role == 'rfp':
        prompt_runner = RFPPromptRunner()
    elif doc_role == 'proposal':
        prompt_runner = ProposalPromptRunner()
    else:
        raise NotImplementedError(f"Need to support doc type {doc_role}")

    try:
        for raw_docextract in raw_docextracts:
            prompt_runner.execute(raw_docextract)
    except Exception as e:
        logger.error(f"Error in gpt_extract: {e}")
        doc_file.processing_status = 'error'
        doc_file.save()
    else:
        doc_file = DocumentFile.objects.get(id=doc_file_id)
        doc_file.processing_status = 'done'
        doc_file.save()
