import openai
import os
import tiktoken

from azurewrapper.gate import Gate

from dotenv import load_dotenv
load_dotenv()

import logging
logger = logging.getLogger('default')


# Todo:
# Engine becomes model == 3.5 or 4
# Encoding becomes internal lookup.

def get_encoding(model='35turbo'):
    return 'cl100k_base'


def get_engine(model, api_type):
    if api_type == 'azure':
        if model == '35turbo':
            return "gpt-35-turbo-16k"
        elif model == 'gpt4':
            return 'gpt-4-32k'
    else:
        if model == '35turbo':
            return "gpt-3.5-turbo-16k"
        elif model == 'gpt4':
            return "gpt-4-1106-preview"



class OpenAIClient:

    def __init__(self, temp=0.7, model='35turbo', gate=None) -> None:
        self.api_type = os.getenv("OPENAI_SOURCE")
        self.engine = get_engine(model, self.api_type)

        openai.api_type = self.api_type

        default_gate = 0.2  # 5 calls/sec

        if self.api_type == "azure":
            default_gate = 5  # 0.2 call/sec
            self._internal_client = openai.AzureOpenAI(
                azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
                api_key=os.getenv("AZURE_OPENAI_KEY"),  
                api_version=os.getenv("AZURE_OPENAI_API_APIVERSION")
            )
        else:
            # Use env variables: 
            self._internal_client = openai.OpenAI()

        self._temp = temp
        self._encoding = get_encoding(model)
        self.max_doc_tokens = 12000  # 16824 total for gpt16k
        if gate is None:
            self.gate = Gate(default_gate)
        else:
            self.gate = gate

    def call(self, messages, temp=None) -> dict:
        self.gate.gate()
        sleep_amt = 60
        while sleep_amt <= 240:
            try:
                response = self._internal_client.chat.completions.create(
                    model=self.engine,
                    messages=messages,
                    temperature=temp or self._temp,
                    max_tokens=self.max_doc_tokens,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None)
            except openai.RateLimitError as e:
                logger.error("Rate limit for OAI. Sleep for %s seconds" % sleep_amt)
                import time
                time.sleep(sleep_amt)
                sleep_amt *= 2
            else:
                return {
                    'response': response.choices[0].message.content,
                    'tokens': response.usage
                }

    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(self._encoding)
        num_tokens = len(encoding.encode(string))
        return num_tokens
