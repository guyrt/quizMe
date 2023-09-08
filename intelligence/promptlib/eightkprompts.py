from ..prompt_types import Prompt, PromptCell


default_system_instruction = """You are a financial assistant who reads SEC 8K filings and answers questions. You should use the doc below and your knowledge of SEC regulations to answer the quesiton.
                   
[startdoc]
{doc_content}
[enddoc]
"""


what_event = Prompt(
    content=[
        PromptCell(role='system', content=default_system_instruction),
        PromptCell(role='user', content="""
What is the event this doc announces? Provide a brief answer. Avoid jargon.
                   
Provide a single sentence in quotes from the doc that best summarizes the event.
                   """)
    ],
    prompt_type="direct"
)

get_embeddable_summary = Prompt(
    content=[
        PromptCell(role='system', content=default_system_instruction),
        PromptCell(role='user', content="""
I am looking for 5 sentences extracted from this document that i can use in a search engine index. Please find and return up to 5 sentences that capture the most important content in this document. Put each sentence on a line with no other content.
                   """)
    ],
    prompt_type='direct'
)

get_entities = Prompt(
    content=[
        PromptCell(role='system', content=default_system_instruction),
        PromptCell(role='user', content="""
Find all People and Companies in this document. 
For each person, list their name, their job, and why they are listed in the doc. Provide a brief snippet from the doc that contains the person and explains your answer. Put each response on a new line.
For each company, list their name and why they are listed in the doc. Provide a brief snippet from the doc that contains the person and explains your answer. Put each response on a new line.
                   
Do not include the Securities and Exchange Commission
                   """)
    ],
    prompt_type='direct+entityupdate' 
)

generate_questions = Prompt(
    content=[
        PromptCell(role='system', content=default_system_instruction),
        PromptCell(role='user', content="""
I am trying to decide whether to invest in the company in this 8-k. List questions that I might ask that can be answered by the document that would help me make an informed decision.
                   
Put one question on each line.
                   """)
    ],
    prompt_type='direct+entityupdate' 
)

find_exhibits = Prompt(
    content=[
        PromptCell(role='system', content=default_system_instruction),
        PromptCell(role='user', content="""
List all exhibits in the doc including the name and a description of what the exhibit is.
                   """)
    ],
    prompt_type='direct+entityupdate' 
)