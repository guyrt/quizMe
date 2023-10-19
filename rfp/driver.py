# main driver for a prompt tree.

from dataclasses import asdict

from azurewrapper.openai_client import OpenAIClient
from azurewrapper.prompt_types import fill_prompt
from rfp.prompts import build_prompts


class RfpDriver:

    def __init__(self) -> None:
        self._oai = OpenAIClient(engine='GPT-4-0314', temp=0.9)

    def run(self, file_loc : str):
        contents = open(file_loc, 'r', encoding='utf8').read()

        prompts = build_prompts(contents)

        for p in prompts:
            response = self._run_prompt(p, contents)
            print(p.name)
            print(response)
            print()
            print()

    def _run_prompt(self, prompt, doc):
        current = fill_prompt(prompt, {'doc_content': doc})
        messages = [asdict(c) for c in current.content]
        raw_response_d = self._oai.call(messages)
        raw_response = raw_response_d['response']
        return raw_response
