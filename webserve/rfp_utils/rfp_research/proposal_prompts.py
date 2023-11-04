from azurewrapper.prompt_types import Prompt, PromptCell

from typing import List


def build_prompts() -> List[Prompt]:

    _default_system_instruction = """You are a bot that helps my company understand proposals. These proposals usually, but not always,
start as a response to a Request for Proposal. 
The contents of a proposal are listed below after the [startdocument] tag.
It contains a mix of important details for this project, key personnel, key dates, and boilerplate that appears in nearly every reponse my company makes.
Your answers should ALWAYS be thorough. Be concise. Be specific in your responses.

[startdocument]
{doc_content}
[enddocument]
""".strip()

    _summarize_ask = Prompt(
        name='ProposalSummarizeAsk',
        content=[
            PromptCell(role='system', content=_default_system_instruction),
            PromptCell(role='user', content="""Describe the project in this RFP. You must always list the company that you are responding to, the key deliverables, and any specific technology packages you will use.""")
        ],
        version=1
    )

    _extract_people = Prompt(
        name='ProposalKeyPeople',
        content=[
            PromptCell(role='system', content=_default_system_instruction),
            PromptCell(role='user', content="""This proposal lists people who will or who might work on the contract if the bid is successful. 
List each person on a new line. Your response should have exactly two lines per person. The first line should be the name and nothing else. 
The second line should list the person's role in the project and key skills.
All people who work on this contract including vendors should be listed.
                       """.strip())
        ],
        version=1
    )

    _extract_questions = Prompt(
        name='ProposalQuestions',
        content=[
            PromptCell(role='system', content=_default_system_instruction),
            PromptCell(role='user', content="""This proposal lists many questions with their answers. Extract all questions and print one question on each line.
Do not make up questions: you should only quote every question from the document. Be sure to list every question that is asked AND ANSWERED in the doc.""".strip())
        ],
        version=1
    )

    return [
        _summarize_ask,
        _extract_people,
        _extract_questions
    ]