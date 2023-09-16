import openai
import os
import tiktoken

from indexgen.gate import Gate

from dotenv import load_dotenv
load_dotenv()


class OpenAIClient:

    def __init__(self, temp=0.7) -> None:
        openai.api_type = "azure"
        openai.api_base = os.getenv("OPENAI_BASE")
        openai.api_version = os.getenv("OPENAI_API_APIVERSION")
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self._engine = "chatGPT_GPT35-turbo-0301"
        self._temp = temp
        self._encoding = 'cl100k_base'
        self.max_doc_tokens = 12000  # 16824 total for gpt16k
        self.gate = Gate(1)  # 1 call/sec

    def call(self, messages) -> str:
        self.gate.gate()
        response = openai.ChatCompletion.create(
            engine=self._engine,
            messages=messages,
            temperature=self._temp,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None)
        return response.choices[0].message.content

    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(self._encoding)
        num_tokens = len(encoding.encode(string))
        return num_tokens
