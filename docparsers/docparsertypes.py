import json 
from datetime import datetime

from dataclasses import dataclass, asdict

@dataclass(slots=True)
class ParsedDoc:

    doc_id : str = None  # guid of the doc
    doc_maker : str = None  # string detailing software used to parse.
    parse_date : str = None  # string date when we parsed.

    # todo - store the version (via git?) of the parser you used.


def serialized_parsed_doc(parsed_doc : ParsedDoc) -> str:
    return json.dumps(asdict(parsed_doc), default=_serialize_datetime)


def _serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')
