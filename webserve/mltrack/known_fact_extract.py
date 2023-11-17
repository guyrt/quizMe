import json
from typing import Dict, List

import bs4
from mltrack.models import ExtractedFact, PromptResponse
from privateuploads.models import DocumentCluster

from .dates_extraction_strategy_tools import merge_tables_of_dates
from .requirement_details_extraction_strategy_tools import merge_tables_of_requirements
from rfp_utils.rfp_research.output_merge import OutputMergeUtility

import logging
logger = logging.getLogger('rqwork')


class KnownFactExtractor:
    """Parse a list of PromptResponses to create known facts."""

    def parse(self, prompt_responses : List[PromptResponse]):
        doc_cluster = self._get_doc_cluster(prompt_responses[0])

        num_deactivated_rows = ExtractedFact.objects.filter(doc_context=doc_cluster).filter(active=True).update(active=False)
        logger.info("Deactivated %s ExtractedFacts", num_deactivated_rows)

        grouped_responses = self._group_chunks(prompt_responses)
        for role, responses in grouped_responses.items():
            role_type = role.replace('_partial', '')  # strip suffix
            if role_type in ('longsummary', 'shortsummary'):
                self._single_per_doc_text_strategy(responses, doc_cluster),
            elif role_type in ('specific_dates', ):
                self._extracted_dates_strategy(responses, doc_cluster)
            elif role_type in ('req_details'):
                self._extracted_details_strategy(responses, doc_cluster)
            else:
                # defaults
                if len(responses) == 1:
                    self._single_per_doc_text_strategy(responses, doc_cluster)
                else:
                    self._merge_many_results(role_type, responses, doc_cluster)

    def _get_doc_cluster(self, prompt_response : PromptResponse) -> DocumentCluster:
        return prompt_response.document_inputs.first().docfile.document

    def _single_per_doc_text_strategy(self, raw_results : List[PromptResponse], doc_cluster : DocumentCluster):
        """Create a KnownFact assuming a single raw_result."""
        if len(raw_results) > 1:
            raise ValueError(f"Unsupported assumption: {raw_results[0].role} has {len(raw_results)} entries but expected one.")

        content = {
            'text': raw_results[0].result
        }
        ExtractedFact.objects.create(
            fact_contents=json.dumps(content),
            output_role=raw_results[0].output_role,
            doc_context=doc_cluster,
            sort_order=0
        )

    def _extracted_details_strategy(self, raw_results : List[PromptResponse], doc_cluster : DocumentCluster):
        """Create a fact for request details type. This is a two col table
        of requirement and section."""
        all_tables = []
        for result in raw_results:
            extracted_tables = self._extract_tables(result)
            logger.info("Extract tables from PromptResponse %s found %s total tables.", result.id, len(extracted_tables))
            all_tables.extend(extracted_tables)
        
        logger.info("Extract req_details merged %s tables.", len(all_tables))
        merged_requirements = merge_tables_of_requirements(all_tables)

        logger.info("Extract req_details strategy merged %s PromptResponses to find %s total rows.", len(raw_results), len(merged_requirements))

        ExtractedFact.objects.create(
            fact_contents=json.dumps({'requirements': merged_requirements}),
            output_role='req_details',
            doc_context=doc_cluster,
            sort_order=0
        )

    def _extracted_dates_strategy(self, raw_results : List[PromptResponse], doc_cluster : DocumentCluster):
        """Create a fact with structured info about dates and their meaning.
        
        Will produce structured output containing two columns: date (str) and description.
        Merge like dates.
        """
        all_date_tables = []
        for result in raw_results:
            all_date_tables.extend(self._extract_tables(result))

        merged_dates = merge_tables_of_dates(all_date_tables)
        ExtractedFact.objects.create(
            fact_contents=json.dumps(merged_dates),
            output_role='specific_dates',
            doc_context=doc_cluster,
            sort_order=0
        )

    def _merge_many_results(self, clean_role: str, raw_results : List[PromptResponse], doc_cluster : DocumentCluster):
        """Merge many string results. For this, you want to use ML merge.
        """
        pr_sample = raw_results[0]
        contents = [r.result for r in raw_results]
        merger = OutputMergeUtility()
        merge_result = merger.run(contents)

        PromptResponse.objects.create(
            template_name=pr_sample.template_name,
            template_version=pr_sample.template_version,
            output_role=clean_role,
            result=merge_result['response'],
            document_inputs=pr_sample.document_inputs,
            prompt_tokens=merge_result['prompt_tokens'],
            completion_tokens=merge_result['completion_tokens'],
            model_service=merger._oai.api_type,
            model_name=merger._oai.engine
        )

        ExtractedFact.objects.create(
            fact_contents=json.dumps({'text': merge_result}),
            output_role=clean_role,
            doc_context=doc_cluster,
            sort_order=0
        )


    def _group_chunks(self, raw_results : List[PromptResponse]) -> Dict[str, List]:
        ret_d : Dict[str, List] = {}
        for r in raw_results:
            out_role = r.output_role
            if out_role not in ret_d:
                ret_d[out_role] = list()
            ret_d[out_role].append(r)
        return ret_d
    
    def _extract_tables(self, prompt_response : PromptResponse):
        html_text = prompt_response.as_html()
        return bs4.BeautifulSoup(html_text, features='lxml').find_all('table')
