from azurewrapper.prompt_types import Prompt, PromptCell

from typing import List


def build_prompts() -> List[Prompt]:

    _default_system_instruction = """You are a bot that helps my company respond to the Request for Proposal (RFP) below. 
The contents of an RFP are listed below after the [startdocument] tag.
The content is a request for proposal. It contains a mix of important details for this project, requirements for response,
and boilerplate that appears in every RFP.
Be concise. Be specific in your responses.

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

    # This is a temporary solution. Too token expensive tbh.
    _extract_details = Prompt(
        name='RFPExtractDetails',
        content=[
            PromptCell(role='system', content=_default_system_instruction),
            PromptCell(role='user', content="""The RFP describes many requirements and questions in my submission to show that I am able to take this business.
I am planning to bid on this RFP. List all requirements I need to fill in the document. Also list all of the questions that I need to answer. 

Respond in a table with two columns:
First column is a requirement. 
Second column is an source for the requirement. This should be a section header from the document.

Source should use document section headers. Use a consistent format for all section headers.

Be thorough and list all requirements and all questions.""")
        ],
        # continuations=[
        #     PromptCell(role='user', content="Are there any more requirements or questions? Don't repeat previous answers. Use the same format."),
        #     PromptCell(role='user', content="Are there any more requirements or questions? Don't repeat previous answers. Use the same format."),
        #     PromptCell(role='user', content="Are there any more requirements or questions? Don't repeat previous answers. Use the same format."),
        #     PromptCell(role='user', content="Create a single table from all of your answers so far. Combine any duplicted requirements or questions. Sometimes, previous answers may not be accurate requirements. In that case, you should remove them.")
        # ],
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

    _certs = Prompt(
        name='RFPCertifications',
        content=[
            PromptCell(role='system', content=_default_system_instruction),
            PromptCell(role='user', content="""List all certifications and specific requirements in this RFP. 

Examples include:
- Required ISO or other accreditations.
- Specific experience expressed as a number of years like "5 years experience with AWS" or "7+ years managing a kitchen with at least 15 staff"
- Board certifications like Medical licenses, Legal license (passed bar), or CPA. Only include if you can find a specific license requirement.
- Legal jurisdictions that apply to the contract.

ONLY include prerequisites if they are specific.

Respond in a table with two columns:
First column is a requirement. 
Second column is an source for the requirement. This should be a section header from the document.

Source should use document section headers. Use a consistent format for all section headers.
                       
Here are some example requirements:
"Demonstration of team members' experience in an Agile framework such as SAFe, Scrum, Kanban, or Lean" -- this mentions specific frameworks.
"ISO-6467 required"  -- this mentions an ISO certification.
"SOC-2 compliance required" -- this is a specific compliance requirement.
                      
Here are some examples that you should NEVER return:
"Submission of pricing information following the guidelines provided" -- this is a requirement for the submission document, not for the contracted work. 
"Description of how changes to this project will be managed" -- this is a requirement for the submission document.
"A copy of each team member’s resume" -- this is a requirement about the submission document.
"Pricing must cover all aspects of the project, including delivery, installation, start-up, and any required equipment or software licenses"
"Each proposal must be submitted in Microsoft Word or Excel, or PDF" -- this is about the submission document.
Only return requirements from the actual document!
""")
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

    return [
        _summarize_ask,
        _specific_dates,
        _certs,
        _expertise,
        _extract_details,
    ]