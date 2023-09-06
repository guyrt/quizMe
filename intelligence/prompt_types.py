from dataclasses import dataclass, asdict

from typing import List


@dataclass
class PromptCell:

    role : str

    content : str


@dataclass
class Prompt:

    content : List[PromptCell]

    prompt_type : str  # eventually use to tell if answer should be parsed. If so, provide parser.
                       # parser can take action: embed+store, parse and add to queue, ect.


def fill_prompt(prompt : Prompt, context):
    return Prompt(
        content = [fill_prompt_cell(p, context) for p in prompt.content],
        prompt_type=prompt.prompt_type
    )


def fill_prompt_cell(cell : PromptCell, context):
    return PromptCell(role=cell.role, content=cell.content.format(**context))


def to_dict(o):
    return asdict(o)
