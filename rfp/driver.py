# main driver for a prompt tree.

from dataclasses import asdict, replace

from azurewrapper.openai_client import OpenAIClient
from azurewrapper.prompt_types import fill_prompt, Prompt, PromptCell
from azurewrapper.gate import Gate
from rfp.prompts import build_prompts

from typing import List


class RfpDriver:

    def __init__(self) -> None:
        self._oai = OpenAIClient(engine='GPT-4-0314', temp=0.9)
        self._gate = Gate(1)

    def run(self, file_loc : str):
        contents = open(file_loc, 'r', encoding='utf8').read()

        prompts = build_prompts(contents)

        for p in prompts:
            responses = self._run_prompt(p, contents)
            print(p.name)
            print(responses)
            print()
            print()

    def _run_prompt(self, prompt : Prompt, doc) -> List[str]:
        prompt = replace(prompt)
        raw_responses = []
        current = fill_prompt(prompt, {'doc_content': doc})
        
        self._gate.gate()
        messages = [asdict(c) for c in current.content]
        raw_response_d = self._oai.call(messages)

        raw_response = raw_response_d['response']
        messages.append(asdict(PromptCell(role='assistant', content=raw_response)))

        raw_responses.append(raw_response)
        while prompt.continuations:
            c = prompt.continuations.pop(0)
            messages.append(asdict(c))
            self._gate.gate()
            raw_response_d = self._oai.call(messages)
            raw_response = raw_response_d['response']
            raw_responses.append(raw_response)
            messages.append(asdict(PromptCell(role='assistant', content=raw_response)))

        return raw_responses
