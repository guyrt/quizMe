import json_repair


def parse_json(input : str):
    if input.startswith('```'):
        input = input[3:-2]

    return json_repair.loads(input)
