

from intelligence.prompt_types import Prompt, PromptCell


def build_entity_prompt(default_system_instruction):

    return Prompt(
        name="GetEntities",
        content=[
            PromptCell(role='system', content=default_system_instruction),
            PromptCell(role='user', content="""Find all People and Companies in this document. 
For each person, list their name, their job, and why they are listed in the doc. Provide a brief snippet from the doc that contains the person and explains your answer. Put each response on a new line.
For each company, list their name and why they are listed in the doc. Provide a brief snippet from the doc that contains the person and explains your answer. Put each response on a new line.
                   
Do not include the Securities and Exchange Commission as a company.
                   
Your output should be in JSON format with three keys: type which is either 'person' or 'company', name, and 'reason' which should say why the entity is in the document.

This is an example of the format:
                   
[
    {{"type": "person", "name": "John Smith", "reason": "The document describes a stock payout to him"}}
    {{"type": "company", "name": "Samsung", "reason": "They were the purchaser in this merger" }},
    {{"type": "company", "name": "Bob's bolts", "reason": "They were purchased in this transaction" }},
]""")
        ],
        prompt_type='direct+entityupdate',
        version=1
    )


def build_doc_questions(default_system_instruction):

    return Prompt(
    name="DocQuestions",
    content=[
        PromptCell(role='system', content=default_system_instruction),
        PromptCell(role='user', content="""I am trying to decide whether to invest in the company in this 8-k. 
List questions that I might ask that can be answered by the document that would help me make an informed decision.

Focus on questions that will help me make an investing decision.

Avoid questions about the date this document was filed.

For each question, provide an answer and a sentence from the doc that will help answer.
                   
This is an example output format:
[
    {{
        "question": "question 1",
        "answer": "answer 1",
        "source": "this is a sentence from the doc"
    }},
    {{
        "question": "question 2",
        "answer": "answer 2",
        "source": "this is a different sentence from the doc"
    }},
    {{
        "question": "question 3",
        "answer": "answer 3",
        "source": "this is a third sentence from the doc"
    }}
]
                   """)
    ],
    prompt_type='direct+questions',
    version=1
)


def build_summary(default_system_instruction):

    return Prompt(
    name='EmbeddableSummary',
    content=[
        PromptCell(role='system', content=default_system_instruction),
        PromptCell(role='user', content="""I am looking up to 5 sentences extracted from this document that I can use in a search engine index. Please find and return up to 5 sections that describe the outcome of this document.
                   
Focus on the new facts this document discusses, not on procedural notes like the date that the meeting took place.

Each section should be around 1 sentence long.

Reply with a list in JSON format. Each element in the list should be a sentence extracted from the doc.

This is an example output format:
[
    "summary sentance 1",
    "summary phrase 2",
    "another summary"
]
                   """)
    ],
    prompt_type='json+direct',
    version=1
)


def build_nondoc_questions(default_system_instruction):
    return Prompt(
    name="NonDocQuestions",
    content=[
        PromptCell(role='system', content=default_system_instruction),
        PromptCell(role='user', content="""I am trying to decide whether to invest in the company in this 8-k. 
List questions that I might ask that CANNOT be answered by the document that would help me make an informed decision.

For each question, suggest other data sources I might want to look at to answer the question

This is an example output format:
[
    "what are the major competitors?",
    "are earnings trending well?",
    "where did the CEO work in the past?"
]
                   """)
    ],
    prompt_type='direct+nondocquestions',
    version=1
)