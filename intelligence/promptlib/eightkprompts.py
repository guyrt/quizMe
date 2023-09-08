from ..prompt_types import Prompt, PromptCell


_default_system_instruction = """You are a financial assistant who reads SEC 8K filings and answers questions. You should use the doc below and your knowledge of SEC regulations to answer the quesiton.
                   
[startdoc]
{doc_content}
[enddoc]
"""


_what_event = Prompt(
    name='8KWhatEvent',
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""
What is the event this doc announces? Provide a brief answer. Avoid jargon.
                   
Provide a single sentence in quotes from the doc that best summarizes the event.
                   """)
    ],
    prompt_type="direct",
    version=1
)

_get_embeddable_summary = Prompt(
    name='8KEmbeddableSummary',
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""
I am looking for 5 sentences extracted from this document that i can use in a search engine index. Please find and return up to 5 sentences that capture the most important content in this document. Put each sentence on a line with no other content.
                   """)
    ],
    prompt_type='direct',
    version=1
)

_get_entities = Prompt(
    name="8KGetEntities",
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""
Find all People and Companies in this document. 
For each person, list their name, their job, and why they are listed in the doc. Provide a brief snippet from the doc that contains the person and explains your answer. Put each response on a new line.
For each company, list their name and why they are listed in the doc. Provide a brief snippet from the doc that contains the person and explains your answer. Put each response on a new line.
                   
Do not include the Securities and Exchange Commission
                   """)
    ],
    prompt_type='direct+entityupdate',
    version=1
)

_generate_doc_questions = Prompt(
    name="8KDocQuestions",
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""
I am trying to decide whether to invest in the company in this 8-k. List questions that I might ask that can be answered by the document that would help me make an informed decision.

Avoid questions about the date this document was filed.

Put one question on each line.
                   """)
    ],
    prompt_type='direct+questions',
    version=1
)

_generate_nondoc_questions = Prompt(
    name="8KNonDocQuestions",
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""
I am trying to decide whether to invest in the company in this 8-k. 
List questions that I might ask that CANNOT be answered by the document that would help me make an informed decision.

For each question, suggest other data sources I might want to look at to answer the question

Put one question on each line.
                   """)
    ],
    prompt_type='direct+nondocquestions',
    version=1
)

_find_exhibits = Prompt(
    name="8KFindExhibits",
    content=[
        PromptCell(role='system', content=_default_system_instruction),
        PromptCell(role='user', content="""
List all exhibits in the doc including the name and a description of what the exhibit is.
                   """)
    ],
    prompt_type='direct+entityupdate',
    version=1
)

eightk_prompts = [
    _what_event,
    _get_entities,
    _get_embeddable_summary,
    _generate_doc_questions,
    _generate_nondoc_questions,
    _find_exhibits
]