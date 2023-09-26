import json

from azurewrapper.openai_client import OpenAIClient


class JsonFixer():

    def __init__(self, num_tries=3) -> None:
        self.oai = OpenAIClient()
        self._num_tries = num_tries

    def run(self, input):
        # Assume that input is a JSON string with some parsing errors. Use an LLM to try to fix it.
        corrections = []
        for i in range(self._num_tries):

            try:
                json.loads(input)
                return input
            except json.JSONDecodeError:
                pass

            import pdb; pdb.set_trace()

            # If we make it here then try to correct.
            prompts = [{'content': main_prompt, 'role': 'system'}]
            for c in corrections:
                prompts.append({'content': input, 'role': 'user'})
                prompts.append({'content': c, 'role': 'assistant'})
                prompts.append({'content': "That is not JSON format", 'role': 'user'})

            prompts.append({'content': input, 'role': 'user'})
            
            response_d = self.oai.call(prompts)
            response = response_d['response']
            corrections.append(response)

        json.loads(input)
            

main_prompt = """You are a bot who formats output in JSON format. You are given input that is almost in JSON format but has
something wrong and doesn't parse. Your job is to create an output that is as close to the input as possible but it valid JSON.

Valid JSON always uses double quotes.
""".strip()