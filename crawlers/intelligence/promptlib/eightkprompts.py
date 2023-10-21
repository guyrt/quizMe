from intelligence.promptlib.common_prompts import build_doc_questions, build_entity_prompt, build_nondoc_questions, build_summary
from ...azurewrapper.prompt_types import Prompt, PromptCell


_default_system_instruction = """You are a financial assistant who reads SEC 8K filings and answers questions. 
You should use the doc below and your knowledge of SEC regulations, filings, and finance to answer the question
                   
[startdoc]
{doc_content}
[enddoc]
"""

_what_event = Prompt(
    name='8KWhatEvent',
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""What is the event this doc announces? Provide a brief answer. Avoid jargon.

On the first line, quote a single sentence in quotes from the doc that best summarizes what the doc is about.

On the next line, provide a brief summary of the material event in the document.
This is an 8-K form filed with the Securities Exchange Commission, so it has a material event.
""")
    ],
    version=1
)


_find_exhibits = Prompt(
    name="8KFindExhibits",
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""List all exhibits in the doc including the name and a description of what the exhibit is.
                   """)
    ],
    version=1
)

eightk_prompts = [
    build_doc_questions(_default_system_instruction),
    build_entity_prompt(_default_system_instruction),
    build_summary(_default_system_instruction),
    _what_event,
    build_nondoc_questions(_default_system_instruction),
    #_find_exhibits
]