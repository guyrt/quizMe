import json
import os
from uuid import uuid4
from azurewrapper.doc_summary_handler import DocSummaryBlobHandler

from azurewrapper.parsed_doc_handler import AzureParsedDocsBlobHandler
from azurewrapper.raw_doc_handler import AzureRawDocsBlobHandler
from azurewrapper.raw_doc_queue import AzureQueueManagerBase
from indexgen.localtypes import (EdgarFile, SecDocRssEntry,
                                 get_sec_entry_from_dict)

from .openai_client import OpenAIClient
from .prompt_types import fill_prompt, to_dict, PromptResponse
from .promptlib.eightkprompts import eightk_prompts


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

        self._peek = True

    def run_from_queue(self):
        """
        Store results.... somewhere. Minimally back into a q_a blob.
        Kick off an "embed this" signal.
        """
        incoming_msg = self._incoming_queue.pop_doc_parse_message(peek=self._peek)
        remote_path = incoming_msg.content
        summary_file_contents = json.loads(self._raw_doc_handler.get_path(remote_path))
        summary = get_sec_entry_from_dict(summary_file_contents)
        
        classify_files = self._classify_files(summary)
        main_file : EdgarFile = classify_files['main']
        main_file_parsed_path = self._get_parsed_path(remote_path, main_file.filename)
        main_file_contents = self._parsed_doc_handler.get_path(main_file_parsed_path)
        
        all_prompts = []
        for prompt, response in self._run_from_content(main_file_contents, main_file.filetype):
            all_prompts.append(
                PromptResponse(
                    id=str(uuid4()),
                    prompt=prompt,
                    response=response,
                    model=self.oai._engine,
                    doc_id=summary.id,
                    cid=summary.cik
                )
            )

        all_prompt_s = [json.dumps(to_dict(s)).replace("\n", "##n##") for s in all_prompts]
        content = '\n'.join(all_prompt_s)
        self._summary_upload_handler.upload_files(main_file_parsed_path, content)
        # just run embeddings straight away? 

    def run_local(self, local_path : str, doc_type : str):
        doc_content = open(local_path, 'r', encoding='utf-8').read()
        self._run_from_content(doc_content, doc_type)

    def _run_from_content(self, content : str, doc_type : str):
        prompts = self._load_initial_prompts(doc_type)
        while len(prompts):
            raw_current = prompts.pop(0)
            current = fill_prompt(raw_current, {'doc_content': content})
            messages = [to_dict(c) for c in current.content]
            yield (raw_current, self.oai.call(messages))

    def _load_initial_prompts(self, doc_type : str):
        if doc_type.lower() == "8-k":
            return eightk_prompts

    def _classify_files(self, entry : SecDocRssEntry):
        main_file = None
        other_files = []
        for file_obj in entry.edgar_files:
            file_type = file_obj.filetype
            if file_type == 'GRAPHIC':
                continue

            if file_type in ('8-K', '10-Q'):  # todo - all files you process.
                main_file = file_obj
            else:
                other_files.append(file_obj)
        return {'main': main_file, 'other': other_files}

    def _get_parsed_path(self, remote_path : str, file_name : str) -> str:
        path_part = os.path.dirname(remote_path)
        return f'{path_part}/{file_name}'
