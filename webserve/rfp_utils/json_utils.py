import json_repair

from typing import Tuple

def find_json(input : str) -> Tuple[str, any, str]:
    """
    Expect strings like:

    something
    
    ```
    <json>
    ```

    something else


    Return the preamble, json, and postamble.
    """

    if "```" not in input:
        return input, [], ""
    
    groups = input.split("```")
    json_section = groups[1]
    if json_section.startswith('json'):
        json_section = json_section[4:]

    obj = json_repair.loads(json_section)
    return groups[0], obj, groups[1]


def parse_json(input : str):
    if input.startswith('```'):
        input = input[3:-2]

    return json_repair.loads(input)
