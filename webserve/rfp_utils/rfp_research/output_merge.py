
from azurewrapper.openai_client import OpenAIClient


from typing import Dict, List


_base_prompt = """User input is a set of outputs from some other system. They all have roughly the same format. They may have some overlap.
Inputs will start wtih a line that says [newinput]. Unique inputs will be separated by a line that says [newinput]

Your job is to create a single output that contains *all* of the content from *all* of the inputs.
This is how you should perform your task:
You can decide to copy a line or combine two lines IF the lines come from different files and cover the same content.
If a line says the document doesn't contain the the information requested, then omit the entire line.
You must copy all lines from all inputs to the output. The only exception is that lines that are combined should not be printed twice.
It is more important to return all information in all inputs than to rephrase or merge inputs.

Here are examples of lines you should not include:
"The document does not contain any specific question and answer format or direct questions that were answered. It primarily outlines the proposal details, responsibilities, deliverables, and timelines." -- Leave this out because it is saying the document doesn't contain specific answers.
"The document does not contain any explicit question and answer format."
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
            'prompt_tokens': raw_response['tokens'].prompt_tokens,
            'completion_tokens': raw_response['tokens'].completion_tokens
        }

    def get_base_with_few_shot(self):
        """Overriddable to add few shots."""
        return _base_prompt
