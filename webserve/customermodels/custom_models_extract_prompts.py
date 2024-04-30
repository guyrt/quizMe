from azurewrapper.prompt_types import Prompt, PromptCell

system = """I'm trying to extract information from the documents I read and put them into a structure. Your job is to help me fill in the table below from the text that the user inputs.

The name of the table you are filling in is "Company Investment Notes".
This is a description of the rows in that table: A list of notes that might be helpful to decide to invest in a company. Each line should be a single fact. Avoid opinions unless you can clearly attribute them to someone.

Return the data in a JSON format with the keys in this example:
[{
    "company name": "A single company's name",
    "stock ticker": "The company's stock ticker. It's ok to fill in stock ticker from your training data.",
    "investment note": "A single fact that could help me to decide to invest or not invest in this company. Examples include information about financial results, information about the industry or industry outlook for this company, changes to their outlook in financial reports, or insights about the products they sell."
}]

You can return as many notes as you need. It's also ok to return zero notes if this format isn't applicable to your data.
"""

quiz_gen = Prompt(
    name="SimpleQuizGen",
    content=[
        PromptCell(role="system", content=system),
        PromptCell(role="user", content="{doc_content}"),
    ],
    version=1,
)




"""I'm trying to extract information from the documents I read and put them into a structure. Your job is to help me fill in the table below from the text that the user inputs.

The name of the table you are filling in is "Large Language Models".
This is a description of the rows in that table: A list of known large language models. Each row must represent a new model name.

Return the data in a JSON format with the keys in this example:
[{
    "model name": "The name of a large language model",
    "model size": "The nubmer of parameters in the model",
    "owner": "A description of the model, including whether it is a Mixture of Experts",
    "license": "License information including whether the model is open source
}]

You can return as many notes as you need. It's also ok to return zero notes if this format isn't applicable to your data.
"""