import json
from azurewrapper.rfp.extractedtext_handler import KMExtractedTextBlobHander
from dataclasses import asdict, replace
from mltrack.models import PromptResponse

from azurewrapper.rfp.extractedtext_handler import KMExtractedTextBlobHander

from privateuploads.models import DocumentExtract

from azurewrapper.openai_client import OpenAIClient
from azurewrapper.gate import Gate

from azurewrapper.prompt_types import fill_prompt, Prompt, PromptCell
from rfp_utils.rfp_research.prompts import build_prompts

from typing import List


class ProposalPromptRunner:

    def __init__(self) -> None:
        self._oai = OpenAIClient(engine='GPT-4-32K-0314', temp=0.9)  # todo make this a setting....
        self._gate = Gate(1)

    def execute(self, doc_extract_id : int):
        doc = DocumentExtract.objects.get(id=doc_extract_id)
        raw_content = KMExtractedTextBlobHander(doc.location_container).get_path(doc.location_path)
        content = self._get_doc_content(raw_content)

        content = content[:60000]  # todo need to parse out like SEC docs.

        for prompt in build_prompts():
            results = self._run_prompt(prompt, content)
            self._process_results(doc, prompt, results)

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

    # todo - extract to a base class.
    def _run_prompt(self, prompt : Prompt, doc) -> List[str]:
        prompt = replace(prompt)
        raw_responses = []
        current = fill_prompt(prompt, {'doc_content': doc})
        
        self._gate.gate()
        messages = [asdict(c) for c in current.content]
        raw_response_d = self._oai.call(messages, prompt.temp)

        raw_response = {
            'response': raw_response_d['response'],
            'prompt_tokens': raw_response_d['tokens']['prompt_tokens'],
            'completion_tokens': raw_response_d['tokens']['completion_tokens']
        }
        messages.append(asdict(PromptCell(role='assistant', content=raw_response_d['response'])))

        raw_responses.append(raw_response)
        while prompt.continuations:
            c = prompt.continuations.pop(0)
            messages.append(asdict(c))
            self._gate.gate()
            raw_response_d = self._oai.call(messages)

            raw_response = {
                'response': raw_response_d['response'],
                'prompt_tokens': raw_response_d['tokens']['prompt_tokens'],
                'completion_tokens': raw_response_d['tokens']['completion_tokens']
            }
            raw_responses.append(raw_response)
            messages.append(asdict(PromptCell(role='assistant', content=raw_response_d['response'])))

        return raw_responses
