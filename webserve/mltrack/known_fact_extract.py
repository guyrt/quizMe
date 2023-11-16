import bs4
from typing import Dict, List
import json

from .dates_extraction_strategy_tools import merge_tables_of_dates
from mltrack.models import PromptResponse


class KnownFactExtractor:
    """Parse a list of PromptResponses to create known facts."""

    def parse(self, prompt_responses : List[PromptResponse]):
        grouped_responses = self._group_chunks(prompt_responses)
        for role, responses in grouped_responses.items():
            role_type = role.replace('_partial', '')  # strip suffix
            if role_type in ('longsummary', 'shortsummary'):
                self._single_per_doc_strategy(responses)
            elif role_type in ('specific_dates'):
                self._extracted_dates_strategy(responses)
            else:
                # defaults
                if len(responses) == 1:
                    self._single_per_doc_strategy(responses)
                else:
                    self._merge_many_results(responses)

    def _single_per_doc_strategy(self, raw_results : List[PromptResponse]):
        """Create a KnownFact assuming a single raw_result."""
        if len(raw_results) > 1:
            raise ValueError(f"Unsupported assumption: {raw_results[0].role} has {len(raw_results)} entries but expected one.")

    def _extracted_dates_strategy(self, raw_results : List[PromptResponse]):
        """Create a fact with structured info about dates and their meaning.
        
        Will produce structured output containing two columns: date (str) and description.
        Merge like dates.
        """
        all_date_tables = []
        for result in raw_results:
            all_date_tables.extend(self._extract_tables(result))

        merged_dates = merge_tables_of_dates(all_date_tables)
        

    def _merge_many_results(self, raw_results : List[PromptResponse]):
        """Merge many results
        
        TODO split to table structures vs not.
        for tables you want to merge the table parts grouped by something.
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
