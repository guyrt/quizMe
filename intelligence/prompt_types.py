from dataclasses import dataclass, asdict

from typing import List, Literal


@dataclass
class Response:

    content : str

    source : Literal['quote', 'generated']  # Quotes are also run through models.


@dataclass
class PromptCell:

    role : str

    content : str


@dataclass
class Prompt:

    name : str

    content : List[PromptCell]

    prompt_type : str  # eventually use to tell if answer should be parsed. If so, provide parser.
                       # parser can take action: embed+store, parse and add to queue, ect.

    version : int


@dataclass
class PromptResponse:

    id : str

    prompt : Prompt

    response : List[Response]

    model : str

    doc_path : str

    summary_path : str

    cid : str


def fill_prompt(prompt : Prompt, context):
    return Prompt(
        name=prompt.name,
        version=prompt.version,
        content = [fill_prompt_cell(p, context) for p in prompt.content],
        prompt_type=prompt.prompt_type
    )


def fill_prompt_cell(cell : PromptCell, context):
    return PromptCell(role=cell.role, content=cell.content.format(**context).strip())  # strip b/c trailing spaces degrade perf.


def to_dict(o):
    return asdict(o)


def promp_response_from_dict(d) -> PromptResponse:
    p = Prompt(
        name=d['prompt']['name'],
        prompt_type=d['prompt']['prompt_type'],
        version=d['prompt']['version'],
        content=[prompt_cell_from_d(c) for c in d['prompt']['content']]
    )
    pr = PromptResponse(
        id=d['id'],
        prompt=p,
        response=responses_from_list(d['response']),
        model=d['model'],
        doc_path=d.get('doc_id', ''),
        summary_path=d.get('summary_path', ''),
        cid=d['cid']
    )
    return pr


def prompt_cell_from_d(d) -> PromptCell:
    pc = PromptCell(
        role=d['role'],
        content=d['content']
    )
    return pc


def responses_from_list(l) -> List[Response]:
    return [
        Response(
            content=d['content'],
            source=d['source']
        ) for d in l
    ]
