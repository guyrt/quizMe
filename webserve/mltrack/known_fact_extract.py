import json
from typing import Dict, List

import bs4
from mltrack.models import ExtractedFact, PromptResponse

from .dates_extraction_strategy_tools import merge_tables_of_dates
from .requirement_details_extraction_strategy_tools import merge_tables_of_requirements


class KnownFactExtractor:
    """Parse a list of PromptResponses to create known facts."""

    def parse(self, prompt_responses : List[PromptResponse]):
        grouped_responses = self._group_chunks(prompt_responses)
        for role, responses in grouped_responses.items():
            role_type = role.replace('_partial', '')  # strip suffix
            if role_type in ('longsummary', 'shortsummary'):
                self._single_per_doc_text_strategy(responses)
            elif role_type in ('specific_dates', ):
                self._extracted_dates_strategy(responses)
            elif role_type in ('req_details'):
                self._extracted_details_strategy(responses)
            else:
                # defaults
                if len(responses) == 1:
                    self._single_per_doc_text_strategy(responses)
                else:
                    self._merge_many_results(responses)

    def _single_per_doc_text_strategy(self, raw_results : List[PromptResponse]):
        """Create a KnownFact assuming a single raw_result."""
        if len(raw_results) > 1:
            raise ValueError(f"Unsupported assumption: {raw_results[0].role} has {len(raw_results)} entries but expected one.")
        content = {
            'text': raw_results[0].result
        }
        ExtractedFact.objects.create(
            fact_contents=json.dumps(content),
            output_role='specific_dates',
            doc_context=raw_results[0].document_inputs.first().docfile.document,
            sort_order=0
        )

    def _extracted_details_strategy(self, raw_results : List[PromptResponse]):
        """Create a fact for request details type. This is a two col table
        of requirement and section."""
        all_tables = []
        for result in raw_results:
            all_tables.extend(self._extract_tables(result))
        
        merged_requirements = merge_tables_of_requirements(all_tables)
        ExtractedFact.objects.create(
            fact_contents=json.dumps(merged_requirements),
            output_role='req_details',
            doc_context=raw_results[0].document_inputs.first().docfile.document,
            sort_order=0
        )

    def _extracted_dates_strategy(self, raw_results : List[PromptResponse]):
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
            doc_context=raw_results[0].document_inputs.first().docfile.document,
            sort_order=0
        )

    def _merge_many_results(self, raw_results : List[PromptResponse]):
        """Merge many results
        
        for strings you want to use ML merge.
        """
        pass

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
        return bs4.BeautifulSoup(html_text).find_all('table')
