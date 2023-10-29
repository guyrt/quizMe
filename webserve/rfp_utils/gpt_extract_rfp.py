from mltrack.models import PromptResponse

from privateuploads.models import DocumentExtract

from azurewrapper.prompt_types import Prompt

from rfp_utils.gpt_base import BasePromptRunner
from rfp_utils.rfp_research.prompts import build_prompts

from typing import List



class RFPPromptRunner(BasePromptRunner):

    def _build_prompts(self):
        return build_prompts()

    def _process_results(self, doc : DocumentExtract, prompt : Prompt, results : List[str]):
        """Handle results - rely on versions to differentiate logic where necessary"""
        if prompt.name == "RFPSummarizeAsk" and prompt.version >= 2:
            r = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role='longsummary',
                result=results[0]['response'],
                prompt_tokens=results[0]['prompt_tokens'],
                completion_tokens=results[0]['completion_tokens']
            )
            r.save()
            r.document_inputs.add(doc)
            r.save()

            r = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role='shortsummary',
                result=results[1]['response'],
                prompt_tokens=results[1]['prompt_tokens'],
                completion_tokens=results[1]['completion_tokens']
            )
            r.save()
            r.document_inputs.add(doc)
            r.save()
        elif prompt.name == 'RFPExtractDetails':
            self._deepdive_extract(doc, prompt, results)
        else:
            # we'll have to break this apart as we get more special cases.
            role = {
                'RFPExtractDetails': 'req_details',
                'RFPSpecificDates': 'specific_dates',
                'RFPLegal': 'legal_notes',
                'RFPCertifications': 'certifications',
                'RFPExpertise': 'expertise',
                'RFPVendors': 'vendors',
                'RFPQA': 'suggested_questions'
            }[prompt.name]

            r = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role=role,
                result=results[-1]['response'],
                prompt_tokens=results[-1]['prompt_tokens'],
                completion_tokens=results[-1]['completion_tokens']
            )
            r.save()
            r.document_inputs.add(doc)
            r.save()

    def _deepdive_extract(self, doc : DocumentExtract, prompt : Prompt, results : List[str]):
        """Parse results, get more details, and produce a link from main table to the subset.
        
        Each detail section is a PromptResponse of new type."""
        pass
