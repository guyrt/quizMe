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
        self.gate = Gate(10)  # 1 call/sec

    def call(self, messages, temperature=0.7) -> str:
        self.gate.gate()
        response = openai.ChatCompletion.create(
            engine="chatGPT_GPT35-turbo-0301",
            messages=messages,
            temperature=temperature,
            max_tokens=4000,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None)
        return response.choices[0].message.content