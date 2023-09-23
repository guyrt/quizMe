from ..prompt_types import Prompt, PromptCell


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
                   
For each risk, provide a single sentence in quotes from the doc that best summarizes the event.
                   """)
    ],
    prompt_type="direct",
    version=1
)

_get_embeddable_summary = Prompt(
    name='QuarterlyEmbeddableSummary',
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""I am looking for 10 sentences extracted from this document that I can use in a search engine index. 
Please find and return up to 10 sentences that capture the most important content in this document.
Put each sentence on a line with no other content.
                   """)
    ],
    prompt_type='direct',
    version=1
)

_get_entities = Prompt(
    name="QuarterlyGetEntities",
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""Find all People and Companies in this document.

For each person, list their name, their job, and why they are listed in the doc. Provide a brief snippet from the doc that contains the person and explains your answer. Put each response on a new line.
For each company, list their name and why they are listed in the doc. Provide a brief snippet from the doc that contains the person and explains your answer. Put each response on a new line.
                   
Do not include the Securities and Exchange Commission
                   """)
    ],
    prompt_type='direct+entityupdate',
    version=1
)

_generate_doc_questions = Prompt(
    name="QuarterlyDocQuestions",
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""I am trying to decide whether to invest in the company in this {doc_type}.
List questions that I might ask that can be answered by the document that would help me make an informed decision.

Avoid questions about the date this document was filed.

Put one question on each line.
                   """)
    ],
    prompt_type='direct+questions',
    version=1
)

_generate_nondoc_questions = Prompt(
    name="QuarterlyNonDocQuestions",
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""I am trying to decide whether to invest in the company in this {doc_type}. 
List questions that I might ask that CANNOT be answered by the document that would help me make an informed decision.

For each question, suggest other data sources I might want to look at to answer the question

Put one question on each line.
                   """)
    ],
    prompt_type='direct+nondocquestions',
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
    prompt_type='direct',
    version=1
)

quarterly_annual_prompts = [
    _risks,
    _get_entities,
    _get_embeddable_summary,
    _generate_doc_questions,
    _generate_nondoc_questions,
    _write_article
]