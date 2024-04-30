from django_rq import job

import logging

from customermodels.models import ExtractionStatusChoices, RawDocumentExtract

logger = logging.getLogger("default")


@job 
def fill_structured_info(structured_info_pk: str):
    try:
        obj = RawDocumentExtract.objects.get(id=structured_info_pk)
    except RawDocumentExtract.DoesNotExist:
        logger.error("fill_structured_info tried to process %s but can't find it.", structured_info_pk)

    if obj.extraction_status == ExtractionStatusChoices.Done:
        logger.info("fill_structured_info tried to process %s but already processed.", structured_info_pk)
        return
    
    