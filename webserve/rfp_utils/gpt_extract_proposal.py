from mltrack.models import PromptResponse

from privateuploads.models import DocumentExtract

from azurewrapper.prompt_types import Prompt
from rfp_utils.gpt_base import BasePromptRunner
from rfp_utils.rfp_research.proposal_prompts import build_prompts

from typing import List


class ProposalPromptRunner(BasePromptRunner):

    def _build_prompts(self):
        return build_prompts()

    def _process_results(self, doc : DocumentExtract, prompt : Prompt, results : List[str]):
        if prompt.name == "ProposalSummarizeAsk" and prompt.version >= 2:
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

        elif prompt.name == 'ProposalKeyPeople':
            # todo - this should chain to go find each person's content, then chain to create special people objects. 
            # But rethink how you chain.
            r = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role='peoplesummary',
                result=results[0]['response'],
                prompt_tokens=results[0]['prompt_tokens'],
                completion_tokens=results[0]['completion_tokens']
            )
            r.save()
            r.document_inputs.add(doc)
            r.save()
