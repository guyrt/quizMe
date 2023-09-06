from .openai_client import OpenAIClient
from .prompt_types import fill_prompt, to_dict
from .promptlib.eightkprompts import what_event, get_embeddable_summary, get_entities, generate_questions, find_exhibits

class DocUnderstandingDriver:

    def __init__(self) -> None:
        self.oai = OpenAIClient()

    def run_local(self, local_path : str, doc_type : str):
        doc_content = open(local_path, 'r', encoding='utf-8').read()
        self._run_from_content(doc_content, doc_type)

    def _run_from_content(self, content : str, doc_type : str):
        prompts = self._load_initial_prompts(doc_type)
        while len(prompts):
            current = prompts.pop(0)
            current = fill_prompt(current, {'doc_content': content})
            messages = [to_dict(c) for c in current.content]
            print(self.oai.call(messages))

    def _load_initial_prompts(self, doc_type : str):
        if doc_type.lower() == "8-k":
            return [
                what_event,
                get_embeddable_summary,
                get_entities,
                generate_questions,
                find_exhibits
            ]
