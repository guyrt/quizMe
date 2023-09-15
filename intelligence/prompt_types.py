from dataclasses import dataclass, asdict

from typing import List


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

    response : str

    model : str

    doc_id : str

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
