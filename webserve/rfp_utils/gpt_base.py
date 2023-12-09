import json
from bs4 import BeautifulSoup
from dataclasses import asdict, replace

import markdown

from privateuploads.models import DocumentExtract

from azurewrapper.openai_client import OpenAIClient
from azurewrapper.prompt_types import fill_prompt, Prompt, PromptCell
from azurewrapper.gate import Gate
from mltrack.models import PromptResponse

from .large_doc_splitter import LargeDocSplitter

from collections.abc import Iterator
from typing import List

import logging
logger = logging.getLogger('default')


class BasePromptRunner:

    def __init__(self) -> None:
        self._oai = OpenAIClient(model='gpt4', temp=0.9)  # todo make this a setting....
        self._splitter = LargeDocSplitter(self._oai)
        logger.info("BasePromptRunner init")
        self._gate = Gate(1)
        self.partial_suffix = '_partial'

    def execute(self, doc_extract_id : int) -> Iterator[PromptResponse]:
        doc = DocumentExtract.objects.get(id=doc_extract_id)
        raw_content = doc.get_content()
        content = self._get_doc_content(raw_content)
        content_chunks : List[str] = self._splitter.split(content, 8000)

        logger.info(f"run intelligence on doc %s with %s chunks.", doc_extract_id, len(content_chunks))

        for prompt in self._build_prompts():
            filtered_chunks = self._filter_chunks(prompt, content_chunks)
            
            for chunk in filtered_chunks:
                raw_results = self._run_prompt_on_chunk(prompt, chunk)  # run on chunk no side effect
                raw_parsed_results = self._process_single_result(doc, prompt, raw_results, len(content_chunks))  # save sub prompts

                for rpr in raw_parsed_results:
                    logger.info(f"Created PromptResponse {rpr.id} from {rpr.template_name}@{rpr.template_version} on DocumentExtract {rpr.document_inputs.all()[0].id}")
                    yield rpr                
            
    def _filter_chunks(self, prompt : Prompt, content_chunks : List[str]) -> List[str]:
        """Filter chunk list. Example override is to only care about first chunk."""
        return content_chunks

    def _get_doc_content(self, payload_s : str):
        payload = json.loads(payload_s)
        if not hasattr(payload, 'get'):
            return " ".join(payload)
        format = payload.get('format')
        if format == 'list_str':
            return markdown.markdown(''.join(payload['content']), extensions=['extra'])
        if format == 'html':
            dom = BeautifulSoup(payload['content'], 'xml')
            return dom.get_text()  # for now... need a proper parser upstream.

        raise ValueError(f"Unepected doc format {format}")

    def _process_single_result(self, doc : DocumentExtract, prompt : Prompt, results : List[str], num_chunks : int) -> List[PromptResponse]:
        """Handle results - rely on versions to differentiate logic where necessary.        
        """
        raise NotImplementedError()

    def _build_prompts(self):
        raise NotImplementedError()

    def _run_prompt_on_chunk(self, prompt : Prompt, doc : str) -> List[dict]:
        prompt = replace(prompt)
        raw_responses = []
        current = fill_prompt(prompt, {'doc_content': doc})
        
        self._gate.gate()
        messages = [asdict(c) for c in current.content]
        raw_response_d = self._oai.call(messages, prompt.temp)

        raw_response = {
            'response': raw_response_d['response'],
            'prompt_tokens': raw_response_d['tokens'].prompt_tokens,
            'completion_tokens': raw_response_d['tokens'].completion_tokens
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
                'prompt_tokens': raw_response_d['tokens'].prompt_tokens,
                'completion_tokens': raw_response_d['tokens'].completion_tokens
            }
            raw_responses.append(raw_response)
            messages.append(asdict(PromptCell(role='assistant', content=raw_response_d['response'])))

        return raw_responses
