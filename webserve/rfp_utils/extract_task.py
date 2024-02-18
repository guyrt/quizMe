import logging
from typing import List

from django_rq import job
from mltrack.models import PromptResponse
from privateuploads.models import DocumentFile, DocumentCluster

from .gpt_extract_proposal import ProposalPromptRunner
from .gpt_extract_rfp import RFPPromptRunner
from mltrack.rfpstuff.known_fact_extract import KnownFactExtractor

logger = logging.getLogger('default')

@job
def gpt_extract(raw_docextracts : List[int], doc_cluster_id):
    all_prompt_responses : List[PromptResponse] = []

    for doc_file in DocumentFile.objects.filter(active=1).filter(document__pk=doc_cluster_id):
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
            for raw_docextract in raw_docextracts:  # todo - consider a change here. You'll need to regroup prompts.
                for response in prompt_runner.execute(raw_docextract):
                    all_prompt_responses.append(response)

        except Exception as e:
            logger.error("Error in gpt_extract: %s", str(e), exc_info=True)
            doc_file.processing_status = 'error'
            doc_file.save()
        else:
            doc_file = DocumentFile.objects.get(id=doc_file.pk)
            doc_file.processing_status = 'done'
            doc_file.save()

    # Directly parse.
    KnownFactExtractor().parse(all_prompt_responses)


@job
def create_known_facts_from_cluster(doc_cluster_id : int):
    doc_cluster = DocumentCluster.objects.get(id=doc_cluster_id)
    prompts = list(PromptResponse.objects.filter(document_inputs__docfile__document=doc_cluster).filter(document_inputs__active=1))
    KnownFactExtractor().parse(prompts)
