from mltrack.models import PromptResponse

from privateuploads.models import DocumentExtract

from azurewrapper.prompt_types import Prompt

from rfp_utils.gpt_base import BasePromptRunner
from rfp_utils.rfp_research.prompts import build_prompts

from typing import List

import logging
logger = logging.getLogger('default')


class RFPPromptRunner(BasePromptRunner):

    def _build_prompts(self):
        return build_prompts()

    def _process_single_result(self, doc : DocumentExtract, prompt : Prompt, results : List[str], num_chunks : int) -> List[PromptResponse]:
        suffix = self.partial_suffix if num_chunks > 1 else ''
        
        logger.info("Processing chunk for %s@%s", prompt.name, prompt.version)

        if prompt.name == "RFPSummarizeAsk" and prompt.version >= 2:
            r = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role='longsummary' + suffix,
                result=results[0]['response'],
                prompt_tokens=results[0]['prompt_tokens'],
                completion_tokens=results[0]['completion_tokens'],
                model_service=self._oai.api_type,
                model_name=self._oai.engine
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
                completion_tokens=results[1]['completion_tokens'],
                model_service=self._oai.api_type,
                model_name=self._oai.engine
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

            total_prompt_tokens = sum([int(d['prompt_tokens']) for d in results])
            total_completion_tokens = sum([int(d['completion_tokens']) for d in results])

            r = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role=role + suffix,
                result=results[-1]['response'],
                prompt_tokens=total_prompt_tokens,
                completion_tokens=total_completion_tokens,
                model_service=self._oai.api_type,
                model_name=self._oai.engine
            )
            r.save()
            r.document_inputs.add(doc)
            r.save()
            return [r]

    def _filter_chunks(self, prompt: Prompt, content_chunks: List[str]) -> List[str]:
        if prompt.name == "RFPSummarizeAsk":
            return content_chunks[:1]
        return super()._filter_chunks(prompt, content_chunks)

    def _deepdive_extract(self, doc : DocumentExtract, prompt : Prompt, results : List[any], suffix):
        """
        TODO: Parse results, get more details, and produce a link from main table to the subset.
        
        Each detail section is a PromptResponse of new type."""

        total_prompt_tokens = sum([int(d['prompt_tokens']) for d in results])
        total_completion_tokens = sum([int(d['completion_tokens']) for d in results])

        # for now, do boring thing.
        r = PromptResponse(
            template_name=prompt.name,
            template_version=prompt.version,
            output_role='req_details' + suffix,
            result=results[-1]['response'],
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_completion_tokens,
            model_service=self._oai.api_type,
            model_name=self._oai.engine
        )
        r.save()
        r.document_inputs.add(doc)
        r.save()
        return [r]
