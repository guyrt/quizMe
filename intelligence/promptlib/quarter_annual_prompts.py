from intelligence.promptlib.common_prompts import build_doc_questions, build_entity_prompt, build_nondoc_questions, build_summary
from ...azurewrapper.prompt_types import Prompt, PromptCell


_default_system_instruction = """You are a financial assistant who reads SEC {doc_type} filings and answers questions from an analyst.
You should use the doc below and your knowledge of SEC regulations, filings, and finance to answer the question.

This document is a snippet, so it's possible that not all questions can be answered from the document. If you can't answer the question,
answer with NO DATA.
Do not guess.

[startdoc]
{doc_content}
[enddoc]
"""


_risks = Prompt(
    name='QuarterlyRisks',
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""This document may contain risks to the business. If so, please list them. List each distinct risk on its own line.

For each risk, quote a passage from the doc that best summarizes the risk. Use JSON format.
                   
This is an example output format:
[
    {{
        "risk": "risk 1",
        "source": "this is a passage from the doc supporting this risk"
    }},
    {{
        "risk": "risk 2",
        "source": "this is a different passage from the doc supporting this risk."
    }}
]
                   """)
    ],
    version=1
)


_write_article = Prompt(
    name="QuarterlyReporter",
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""Pretend you are a financial journalist. 
Your job is to write an analysis piece about this company from the data you have in the document.
                   
Write a 1 or 2 paragraph article in the style of The Economist. 
                   
Do not regurgitate facts. Your job is to synthesize the content and its meaning in a broader market, taking into account your
knowledge of the industry this company is in.""")
    ],
    version=1
)

quarterly_annual_prompts = [
    _risks,
    build_entity_prompt(_default_system_instruction),
    build_summary(_default_system_instruction),
    build_doc_questions(_default_system_instruction),
    build_nondoc_questions(_default_system_instruction),
    _write_article
]