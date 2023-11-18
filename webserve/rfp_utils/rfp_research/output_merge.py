from azurewrapper.openai_client import OpenAIClient


from typing import Dict, List


_base_prompt = """User input is a set of outputs from some other system. They all have roughly the same format. They may have some overlap.

Your job is to create a single output that contains *all* of the content from *all* of the inputs.
It is more important to return all information in all inputs than to rephrase or merge inputs.

Here are examples of lines you should not include:
"The document does not contain any specific question and answer format or direct questions that were answered. It primarily outlines the proposal details, responsibilities, deliverables, and timelines." -- Leave this out because it is saying the document doesn't contain specific answers.
"The document does not contain any explicit question and answer format."
"""


class OutputMergeUtility:

    def __init__(self, gate=None) -> None:
        self._oai = OpenAIClient(gate=gate, model='35turbo')

    def run(self, inputs : List[str]) -> Dict:
        """
        Given list of previous outputs, merge to a single output with same format.

        Run merge logic. 
        """
        base = self.get_base_with_few_shot()
        user_input = "\n".join(inputs)

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
