import json
from azurewrapper.prompt_types import Prompt, PromptCell
from customermodels.models import UserTable

system = """I'm trying to extract information from the documents I read and put them into a structure. Your job is to help me fill in the table below from the text that the user inputs.

The name of the table you are filling in is "{table_name}".
This is a description of the rows in that table: {table_description}.

Return the data in a JSON format with the keys in this example:
{format}

You can return as many notes as you need. It's also ok to return zero notes if this format isn't applicable to your data.
"""


def build_prompt_from_user_table(source : UserTable, doc_content : str):
    raw_cols = [{
        c.name: c.description for c in source.usertablecolumn_set.all()
    }]
    json_format = json.dumps(raw_cols) # perplexity claims no need to format!
    system_prompt = system.format(table_name=source.name, table_description=source.description, format=json_format)
    prompt = Prompt(
        name="DataExtraction",
        content=[
            PromptCell(role="system", content=system_prompt),
            PromptCell(role="user", content=f"{doc_content}"),
        ],
        version=1,
    )
    return prompt




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