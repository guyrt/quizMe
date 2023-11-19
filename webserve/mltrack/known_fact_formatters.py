import json

from typing import List

def format_specific_date_to_object(raw_content : str) -> List:
    """format a specific date set as a table for html output"""
    date_content = json.loads(raw_content)
    keys = sorted(date_content.keys())  # assume shape is Dict with key of date and value of reason.  Format sorts well.

    return [[k, date_content[k]] for k in keys]


def format_requirements(raw_content : str) -> List:
    req_contents = json.loads(raw_content)
    rows = req_contents.get('requirements')
    if not rows:
        return []
    rows = sorted(rows, key=lambda x: x['section'])
    return rows
