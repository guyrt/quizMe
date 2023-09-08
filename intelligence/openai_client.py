import openai
import os
from indexgen.gate import Gate

from dotenv import load_dotenv
load_dotenv()


class OpenAIClient:

    def __init__(self) -> None:
        openai.api_type = "azure"
        openai.api_base = os.getenv("OPENAI_BASE")
        openai.api_version = os.getenv("OPENAI_API_APIVERSION")
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self._engine = "chatGPT_GPT35-turbo-0301"
        self._temp = 0.7
        self.gate = Gate(1)  # 1 call/sec

    def call(self, messages) -> str:
        self.gate.gate()
        response = openai.ChatCompletion.create(
            engine=self._engine,
            messages=messages,
            temperature=self._temp,
            max_tokens=4000,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None)
        return response.choices[0].message.content
