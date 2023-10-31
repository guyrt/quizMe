from mltrack.models import PromptResponse

from privateuploads.models import DocumentExtract

from azurewrapper.prompt_types import Prompt

from rfp_utils.gpt_base import BasePromptRunner
from rfp_utils.rfp_research.prompts import build_prompts

from typing import List



class RFPPromptRunner(BasePromptRunner):

    def _build_prompts(self):
        return build_prompts()

    def _process_single_result(self, doc : DocumentExtract, prompt : Prompt, results : List[str]):
        suffix = self.partial_suffix if len(results) > 1 else ''
        
        if prompt.name == "RFPSummarizeAsk" and prompt.version >= 2:
            r = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role='longsummary' + suffix,
                result=results[0]['response'],
                prompt_tokens=results[0]['prompt_tokens'],
                completion_tokens=results[0]['completion_tokens']
            )
            r.save()
            r.document_inputs.add(doc)
            r.save()

            r2 = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role='shortsummary' + suffix,
                result=results[1]['response'],
                prompt_tokens=results[1]['prompt_tokens'],
                completion_tokens=results[1]['completion_tokens']
            )
            r2.save()
            r2.document_inputs.add(doc)
            r2.save()
            return [r, r2]
        elif prompt.name == 'RFPExtractDetails':
            return self._deepdive_extract(doc, prompt, results, suffix)
        else:
            # we'll have to break this apart as we get more special cases.
            role = {
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
                output_role=role + suffix,
                result=results[-1]['response'],
                prompt_tokens=results[-1]['prompt_tokens'],
                completion_tokens=results[-1]['completion_tokens']
            )
            r.save()
            r.document_inputs.add(doc)
            r.save()
            return [r]

    def _filter_chunks(self, prompt: Prompt, content_chunks: List[str]) -> List[str]:
        if prompt.name == "RFPSummarizeAsk":
            return content_chunks[:1]
        return super()._filter_chunks(prompt, content_chunks)

    def _deepdive_extract(self, doc : DocumentExtract, prompt : Prompt, results : List[str], suffix):
        """
        TODO: Parse results, get more details, and produce a link from main table to the subset.
        
        Each detail section is a PromptResponse of new type."""

        # for now, do boring thing.
        r = PromptResponse(
            template_name=prompt.name,
            template_version=prompt.version,
            output_role='req_details' + suffix,
            result=results[-1]['response'],
            prompt_tokens=results[-1]['prompt_tokens'],
            completion_tokens=results[-1]['completion_tokens']
        )
        r.save()
        r.document_inputs.add(doc)
        r.save()
        return [r]
