import json
from bs4 import BeautifulSoup
from dataclasses import asdict, replace

from privateuploads.models import DocumentExtract

from azurewrapper.openai_client import OpenAIClient
from azurewrapper.prompt_types import fill_prompt, Prompt, PromptCell
from azurewrapper.gate import Gate
from mltrack.models import PromptResponse
from rfp_utils.rfp_research.output_merge import OutputMergeUtility

from .large_doc_splitter import LargeDocSplitter


from typing import List

import logging
logger = logging.getLogger('rqwork')


class BasePromptRunner:

    partial_suffix = '_partial'

    def __init__(self) -> None:
        self._oai = OpenAIClient(engine='GPT-4-32K-0314', temp=0.9)  # todo make this a setting....
        self._splitter = LargeDocSplitter(self._oai)
        logger.info("BasePromptRunner init")
        self._gate = Gate(1)

    def execute(self, doc_extract_id : int):
        doc = DocumentExtract.objects.get(id=doc_extract_id)
        raw_content = doc.get_content()
        content = self._get_doc_content(raw_content)
        content_chunks : List[str] = self._splitter.split(content, 8000)

        logger.info(f"run intelligence on doc %s with %s chunks.", doc_extract_id, len(content_chunks))

        for prompt in self._build_prompts():
            filtered_chunks = self._filter_chunks(prompt, content_chunks)
            raw_result_list = []
            for chunk in filtered_chunks:
                raw_results = self._run_prompt_on_chunk(prompt, chunk)  # run on chunk no side effect
                raw_parsed_results = self._process_single_result(doc, prompt, raw_results)  # save sub prompts
                raw_result_list.extend(raw_parsed_results)
            chunk_groups = self._group_chunks(raw_result_list)
            for g in chunk_groups.values():
                self._merge_chunks(prompt, doc, g)  # merge and save

    def _filter_chunks(self, prompt : Prompt, content_chunks : List[str]) -> List[str]:
        """Filter chunk list. Example override is to only care about first chunk."""
        return content_chunks

    def _get_doc_content(self, payload_s : str):
        payload = json.loads(payload_s)
        if not hasattr(payload, 'get'):
            return " ".join(payload)
        format = payload.get('format')
        if format == 'list_str':
            return ' '.join(payload['content'])
        if format == 'html':
            dom = BeautifulSoup(payload['content'], 'xml')
            return dom.get_text()  # for now... need a proper parser upstream.

        raise ValueError(f"Unepected doc format {format}")

    def _group_chunks(self, raw_results : List[PromptResponse]):
        ret_d = {}
        for r in raw_results:
            out_role = r.output_role
            if out_role not in ret_d:
                ret_d[out_role] = []
            ret_d[out_role].append(r)
        return ret_d

    def _merge_chunks(self, prompt : Prompt, doc : DocumentExtract, raw_results : List[PromptResponse]):
        pr = raw_results[0]
        new_role = pr.output_role.replace(self.partial_suffix, '')

        logger.info("Merging %s chunks for prompt %s@%s role %s", len(raw_results), prompt.name, prompt.version, new_role)

        if len(raw_results) == 1:
            pr = raw_results[0]
            pr.output_role = new_role
            pr.save()
            return
        else:
            raw_response = OutputMergeUtility(gate=self._oai.gate).run([r.result for r in raw_results])
            
            r = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role=new_role,
                result=raw_response['response'],
                prompt_tokens=raw_response['prompt_tokens'],
                completion_tokens=raw_response['completion_tokens']
            )
            r.save()
            r.document_inputs.add(doc)
            r.save()

    def _process_single_result(self, doc : DocumentExtract, prompt : Prompt, results : List[str]):
        """Handle results - rely on versions to differentiate logic where necessary.
        
        These shoul
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
