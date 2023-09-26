

from typing import List
from intelligence.prompt_types import Response


def get_answer_parser(prompt_name : str, response : str) -> List[Response]:
    if prompt_name == "8KWhatEvent":
        return WhatEventParser().parse_response(response)
    
    raise ValueError(f"No prompt parser found for {prompt_name}")
    



class Parser:

    def parse_response(response : str) -> List[Response]:
        # TODO: figure out how to add new prompts with data...
        # this should be the prompt and dict of inputs alongside.
        raise NotImplementedError()



class WhatEventParser(Parser):

    def parse_response(response: str) -> List[Response]:
        lines = [l for l in response.splitlines() if l]
        assert len(lines) == 2

        quote = lines[0]
        summary = lines[1]
        if quote[0] == '"' and quote[-1] == '"':
            quote = quote[1:-1]
        
        responses = [
            Response(
                content=quote,
                source="quote"
            ),
            Response(
                content=summary,
                source="generated"
            )
        ]
        return responses
