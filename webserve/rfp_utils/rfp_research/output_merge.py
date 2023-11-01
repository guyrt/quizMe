
from azurewrapper.openai_client import OpenAIClient


from typing import Dict, List


_base_prompt = """User input is a set of outputs from some other system. They all have roughly the same format. They may have some overlap.
Inputs will start wtih a line that says [newinput]. Unique inputs will be separated by a line that says [newinput]

Your job is to create a single output that contains *all* of the content from *all* of the inputs.
This is how you should perform your task:
You can decide to copy a line or merge two lines IF the lines come from different files and cover the exact same content.
You must coyp all lines from all inputs to the output UNLESS you opted to merge the lines.
It is more important to return all information in all inputs than to rephrase or merge inputs.
"""


class OutputMergeUtility:

    def __init__(self, gate) -> None:
        self._oai = OpenAIClient(gate=gate) # todo make this default to turbo

    def run(self, inputs : List[str]) -> Dict:
        """
        Given list of previous outputs, merge to a single output with same format.

        Run merge logic. 
        """
        base = self.get_base_with_few_shot()
        user_input = "[newinput]" + "\n[newinput]\n".join(inputs)

        raw_response = self._oai.call(
            [
                {'role': 'system', 'content': base},
                {'role': 'user', 'content': user_input}
            ]
        )

        return {
            'response': raw_response['response'],
            'prompt_tokens': raw_response['tokens']['prompt_tokens'],
            'completion_tokens': raw_response['tokens']['completion_tokens']
        }

    def get_base_with_few_shot(self):
        """Overriddable to add few shots."""
        return _base_prompt
