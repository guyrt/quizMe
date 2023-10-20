from dataclasses import asdict
import json
import os
from typing import List
from uuid import uuid4

from azurewrapper.doc_summary_handler import DocSummaryBlobHandler
from azurewrapper.openai_client import OpenAIClient
from azurewrapper.parsed_doc_handler import AzureParsedDocsBlobHandler
from azurewrapper.raw_doc_handler import AzureRawDocsBlobHandler
from azurewrapper.raw_doc_queue import AzureQueueManagerBase
from indexgen.localtypes import (EdgarFile, SecDocRssEntry,
                                 get_sec_entry_from_dict)
from intelligence.answer_parsers import retrieve_parsed_answer
from intelligence.large_doc_parser import LargeDocParser

from ..azurewrapper.prompt_types import PromptResponse, Response, fill_prompt, to_dict
from .promptlib.eightkprompts import eightk_prompts
from .promptlib.quarter_annual_prompts import quarterly_annual_prompts


class DocUnderstandingDriver:

    def __init__(self, 
                 raw_doc_handler: AzureRawDocsBlobHandler, 
                 incoming_queue : AzureQueueManagerBase,
                 parsed_doc_handler : AzureParsedDocsBlobHandler,
                 summary_upload_handler : DocSummaryBlobHandler) -> None:
        self.oai = OpenAIClient()
        self._raw_doc_handler = raw_doc_handler
        self._incoming_queue = incoming_queue
        self._parsed_doc_handler = parsed_doc_handler
        self._summary_upload_handler = summary_upload_handler

        self._peek = False

    def run_from_queue(self):
        """
        Store results.... somewhere. Minimally back into a q_a blob.
        Kick off an "embed this" signal.
        """
        incoming_msg = self._incoming_queue.pop_doc_parse_message(peek=self._peek)
        remote_summary_path = incoming_msg.content
        summary_file_contents = json.loads(self._raw_doc_handler.get_path(remote_summary_path))
        summary = get_sec_entry_from_dict(summary_file_contents)
        
        classify_files = self._classify_files(summary)
        main_file : EdgarFile = classify_files['main']
        main_file_parsed_path = self._get_parsed_path(remote_summary_path, main_file.filename)
        print(main_file_parsed_path)
        main_file_contents = self._parsed_doc_handler.get_path(main_file_parsed_path)
        
        print(f"Running on {summary.cik}: {main_file.url}")

        all_prompts = []
        for prompt, responses in self._run_from_content(main_file_contents, main_file.filetype):
            if not responses:
                continue
            responses = self._clean_responses(responses)

            all_prompts.append(
                PromptResponse(
                    id=str(uuid4()),
                    prompt=prompt,
                    response=responses,
                    model=self.oai._engine,
                    doc_path=main_file_parsed_path,
                    summary_path=remote_summary_path,
                    cid=summary.cik
                )
            )

        all_prompt_s = [json.dumps(asdict(s)) for s in all_prompts]
        content = '\n'.join(all_prompt_s)
        self._summary_upload_handler.upload_files(main_file_parsed_path, content)

    def run_local(self, local_path : str, doc_type : str):
        doc_content = open(local_path, 'r', encoding='utf-8').read()
        for prompt, raw_response in self._run_from_content(doc_content, doc_type):
            yield PromptResponse(
                        id=str(uuid4()),
                        prompt=prompt,
                        response=raw_response,
                        model=self.oai._engine,
                        doc_path='local',
                        summary_path='local',
                        cid='local'
                    )

    def _clean_responses(self, responses : List[Response]) -> List[Response]:
        for r in responses:
            r.content = r.content.replace("\n", "##n##")
        return responses

    def _run_from_content(self, content : str, doc_type : str):

        # split your content.
        total_size = self.oai.num_tokens_from_string(content)
        if total_size > self.oai.max_doc_tokens:
            chunks = LargeDocParser(self.oai).split(content, self.oai.max_doc_tokens)
        else:
            chunks = [content]

        for chunk in chunks:
            prompts = self._load_initial_prompts(doc_type)
            while len(prompts):
                raw_current = prompts.pop(0)
                current = fill_prompt(raw_current, {'doc_content': chunk, 'doc_type': doc_type})
                messages = [to_dict(c) for c in current.content]
                
                raw_response_d = self.oai.call(messages)
                raw_response = raw_response_d['response']
                all_responses = retrieve_parsed_answer(raw_current.name, raw_response)
                # todo: you need to iterate through continuations.
                # for each, you'll want to add to the responses, then execute, then retrieve_parsed_answer.

                # Call response parser logic and return each Response object.
                # TODO: tokens including JSON fix.
                yield (raw_current, all_responses)

    def _load_initial_prompts(self, doc_type : str):
        if doc_type.lower() in ("8-k", '8-k/a'):
            return list(eightk_prompts)
        if doc_type.lower() in ('10-k', '10-q'):
            return list(quarterly_annual_prompts)
        return []

    def _classify_files(self, entry : SecDocRssEntry):
        main_file = None
        other_files = []
        for file_obj in entry.edgar_files:
            file_type = file_obj.filetype
            if file_type == 'GRAPHIC':
                continue

            if file_type in ('8-K', '8-K/A', '10-Q', "10-K", '6-K'):  # todo - all files you process.
                main_file = file_obj
            else:
                other_files.append(file_obj)
        return {'main': main_file, 'other': other_files}

    def _get_parsed_path(self, remote_path : str, file_name : str) -> str:
        path_part = os.path.dirname(remote_path)
        return f'{path_part}/{file_name}'
