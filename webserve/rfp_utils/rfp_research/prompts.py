from azurewrapper.prompt_types import Prompt, PromptCell

from typing import List


def build_prompts() -> List[Prompt]:

    _default_system_instruction = """You are a bot that helps my company respond to the Request for Proposal (RFP) below. 
The contents of an RFP are listed below after the [startdocument] tag.
The content is a request for proposal. It contains a mix of important details for this project, requirements for response,
and boilerplate that appears in every RFP.
Your answers should ALWAYS be thorough. Be concise. Be specific in your responses.

[startdocument]
{doc_content}
[enddocument]
""".strip()

    _summarize_ask = Prompt(
        name='RFPSummarizeAsk',
        content=[
            PromptCell(role='system', content=_default_system_instruction),
            PromptCell(role='user', content="""Describe the project in this RFP""")
        ],
        continuations=[
            PromptCell(role='user', content="write a headline length summary of your last response. Focus on who, what, when, and how much."),
        ],
        version=2
    )

    _extract_details = Prompt(
        name='RFPExtractDetails',
        content=[
            PromptCell(role='system', content=_default_system_instruction),
            PromptCell(role='user', content="""The RFP describes many requirements in my submission to show that I am able to take this business. I am planning to bid on this RFP. List all requirements I need to fill in the document. Use a table with two columns. First column is a requirement. Second column is an attribution. Attributions should list document sections. Be thorough and list all requirements.""")
        ],
        continuations=[
            PromptCell(role='user', content="Are there any more? Don't repeat previous answers. Use the same format."),
            PromptCell(role='user', content="Are there any more? Don't repeat previous answers. Use the same format."),
            PromptCell(role='user', content="Create a single table from all of your answers so far. Combine any duplicted requirements. Sometimes, previous answers may not be accurate requirements. In that case, you should remove them.")
        ],
        version=1
    )

    _specific_dates = Prompt(
        name='RFPSpecificDates',
        content=[
            PromptCell(role='system', content=_default_system_instruction),
            PromptCell(role='user', content="""Make a table of all dates in this text selection. The table should have two columns. First list the date in "yyyy-MM-dd" format. Second list the meaning of the date.""")
        ],
        version=1
    )

    _legal = Prompt(
        name='RFPLegal',
        content=[
            PromptCell(role='system', content=_default_system_instruction),
            PromptCell(role='user', content="""What legal jurisdictions apply to this RFP?""")
        ],
        version=1
    )

    _certs = Prompt(
        name='RFPCertifications',
        content=[
            PromptCell(role='system', content=_default_system_instruction),
            PromptCell(role='user', content="""Are there any required certifications or prerequisites for responders to this RFP?""")
        ],
        version=1
    )

    _expertise = Prompt(
        name='RFPExpertise',
        content=[
            PromptCell(role='system', content=_default_system_instruction),
            PromptCell(role='user', content="""What expertise will vendors need to demonstrate to bid for this project?""")
        ],
        version=1
    )
    
    _vendors = Prompt(
        name='RFPVendors',
        content=[
            PromptCell(role='system', content=_default_system_instruction),
            PromptCell(role='user', content="""For any technology requirements, list popular vendors that provide that kind of software.""")
        ],
        version=1
    )

    _qa = Prompt(
        name='RFPQA',
        content=[
            PromptCell(role='system', content=_default_system_instruction),
            PromptCell(role='user', content="""I am sending a list of questions to the RFP author to help me write a winning proposal. What questions should I ask to clarify requirements or understand their needs in more detail? Do not ask questions that can be answered by the document itself.""")
        ],
        version=1
    )

    return [
        _summarize_ask,
        _extract_details,
        _specific_dates,
        _legal,
        _certs,
        _expertise,
        _vendors,
        _qa
    ]