import json

from typing import Any, List
from intelligence.prompt_types import Response
from intelligence.prompt_utils import JsonFixer


def retrieve_parsed_answer(prompt_name : str, response : str) -> List[Response]:
    if prompt_name == "8KWhatEvent":
        return WhatEventParser().parse_response(response)
    if prompt_name in ("EmbeddableSummary"):
        return JsonListOfStringsParser().parse_response(response)
    if prompt_name == "DocQuestions":
        return DocQuestionsParse().parse_response(response)
    if prompt_name == "GetEntities":
        return GetEntities().parse_response(response)
    if prompt_name in ('NonDocQuestions', 'QuarterlyReporter'):
        return Parser().parse_response(response)
    if prompt_name in ('QuarterlyRisks'):
        return RisksParser().parse_response(response)
    
    raise ValueError(f"No prompt parser found for {prompt_name}")


class Parser:

    def parse_response(self, response : str) -> List[Response]:
        # TODO: figure out how to add new prompts with data...
        # this should be the prompt and dict of inputs alongside.
        
        # noop
        return [
            Response(content=response, source='generated')
        ]


class WhatEventParser(Parser):

    def parse_response(self, response: str) -> List[Response]:
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


class JsonListParse(Parser):

    def __init__(self) -> None:
        super().__init__()
        self._corrector = JsonFixer()

    def _parse_internal(self, data):
        raise NotImplementedError()

    def parse_response(self, response: str) -> List[Response]:
        # TODO: build recovery
        try:
            response = self._corrector.run(response)  # try to correct the problem, or pass through.
            data = json.loads(response)  # todo: we double parse here but not huge deal.
            if isinstance(data, list):
                return self._parse_internal(data)
            
            raise ValueError(f"Expected json list but got {type(data)}")
        except json.JSONDecodeError:
            import pdb; pdb.set_trace()
            a = 1
            

class JsonListOfStringsParser(JsonListParse):

    def _parse_internal(self, data : List[Any]):
        return [
                Response(
                    content=l,
                    source='generated'
                ) for l in data
            ]


class RisksParser(JsonListParse):

    def _parse_internal(self, data):
        responses = []
        for elt in data:
            responses.extend([
                Response(content=elt['risk'], source='generated'),
                Response(content=elt['source'], source='generated')
            ])
        return responses


class DocQuestionsParse(JsonListParse):

    def _parse_internal(self, data) -> List[Response]:
        responses = []
        for elt in data:
            responses.extend([
                Response(
                    content=elt['question'],
                    source='generated'
                ),
                Response(
                    content=elt['answer'],
                    source='generated'
                ),
                Response(
                    content=elt['source'],
                    source='quote'
                )
            ])

        return responses
        

class GetEntities(JsonListParse):

    def _parse_internal(self, data) -> List[Response]:
        responses = []
        for elt in data:
            responses.append(Response(content=f"{elt['name']}: {elt['reason']}", source='generated'))

        return responses
