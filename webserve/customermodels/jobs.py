from dataclasses import asdict
from re import I
from openai.types import CompletionUsage
from uuid import UUID
from django_rq import job

import logging

from azurewrapper.openai_client import OpenAIClient
from customermodels.custom_models_extract_prompts import build_prompt_from_user_table
from customermodels.models import ExtractionStatusChoices, RawDocumentExtract, UserTable
from extensionapis.models import SingleUrl
from mltrack.consumer_prompt_models import UserLevelVectorIndex

logger = logging.getLogger("default")


class FillFromSingleUrlToUserTable:

    def __init__(self) -> None:
        self._return_tokens = 3000
        self._oai = OpenAIClient(
            model="gpt4", temp=0.7, max_doc_tokens=self._return_tokens
        )

    def execute(self, structured_info_pk : UUID):
        try:
            obj = RawDocumentExtract.objects.get(id=structured_info_pk)
        except RawDocumentExtract.DoesNotExist:
            logger.error("fill_structured_info tried to process %s but can't find it.", structured_info_pk)

        if obj.extraction_status == ExtractionStatusChoices.Done:
            logger.info("fill_structured_info tried to process %s but already processed.", structured_info_pk)
            return
        
        self.gate_types(obj)
    
        extraction_target = self.get_extraction(obj)
        source = self.get_source(obj)

        # Execute toolchain (this will get more complicated):

        # Todo - prefilter somehow.

        # Build Prompt
        prompt = self.build_prompt(extraction_target, source)

        # Execute and save prompt run.
        result = self._oai.call([asdict(c) for c in prompt.content])
        response : str = result['response']
        tokens : CompletionUsage = result['tokens']
        import ipdb; ipdb.set_trace()

        # Save results

    def gate_types(self, obj : RawDocumentExtract):
        if obj.extraction_target != 'user_table':
            raise ValueError(f"Unexpected extraction_target {obj.extraction_target}")
        if obj.source_table != 'single_url': 
            raise ValueError(f"Unexpected source_table {obj.source_table}")

    def build_prompt(self, extraction_target : UserTable, source : str):
        return build_prompt_from_user_table(extraction_target, source)

    def get_extraction(self, obj : RawDocumentExtract) -> UserTable:
        # may throw DoesNotExist.
        return UserTable.objects.get(id=obj.extraction_pk)

    def get_source(self, obj : RawDocumentExtract) -> str:
        content = UserLevelVectorIndex.objects.filter(doc_id=obj.source_pk).values_list('doc_chunk', flat=True)
        return '\n'.join(content)


@job 
def fill_structured_info(structured_info_pk: str):
    FillFromSingleUrlToUserTable().execute(structured_info_pk)
