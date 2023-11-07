from mltrack.models import PromptResponse

from privateuploads.models import DocumentExtract

from azurewrapper.prompt_types import Prompt
from rfp_utils.gpt_base import BasePromptRunner
from rfp_utils.rfp_research.proposal_prompts import build_prompts

from typing import List


class ProposalPromptRunner(BasePromptRunner):

    def _build_prompts(self):
        return build_prompts()

    def _filter_chunks(self, prompt: Prompt, content_chunks: List[str]) -> List[str]:
        if prompt.name == "ProposalSummarizeAsk":
            return content_chunks[:1]
        return super()._filter_chunks(prompt, content_chunks)

    def _process_single_result(self, doc : DocumentExtract, prompt : Prompt, results : List[str], num_chunks : int):
        suffix = self.partial_suffix if num_chunks > 1 else ''

        if prompt.name == "ProposalSummarizeAsk":
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
            return [r]

        elif prompt.name == 'ProposalKeyPeople':
            r = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role='peoplesummary' + suffix,
                result=results[0]['response'],
                prompt_tokens=results[0]['prompt_tokens'],
                completion_tokens=results[0]['completion_tokens'],
                model_service=self._oai.api_type,
                model_name=self._oai.engine
            )
            r.save()
            r.document_inputs.add(doc)
            r.save()
            return [r]
        elif prompt.name == 'ProposalQuestions':
            r = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role='proposalquestions' + suffix,
                result=results[0]['response'],
                prompt_tokens=results[0]['prompt_tokens'],
                completion_tokens=results[0]['completion_tokens'],
                model_service=self._oai.api_type,
                model_name=self._oai.engine
            )
            r.save()
            r.document_inputs.add(doc)
            r.save()
            return [r]
        else:
            raise NotImplementedError(f"Unknown prompt {prompt.name}:{prompt.version}")
