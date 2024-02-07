from dataclasses import dataclass, asdict
from datetime import datetime
import json

from typing import List


@dataclass(slots=True)
class EdgarFile:
    filename: str
    filetype: str
    url: str


@dataclass(slots=True)
class SecDocRssEntry:
    doc_type: str  # 8-k ect
    title: str
    zip_link: str
    published: datetime
    id: str  # usually the file name.
    cik: str
    edgar_files: List[EdgarFile]
    company_name: str
    edgar_assistantdirector: str


def get_sec_entry_from_dict(entry) -> SecDocRssEntry:
    edgar_files = [EdgarFile(**e) for e in entry["edgar_files"]]
    entry["edgar_files"] = edgar_files
    return SecDocRssEntry(**entry)


def serialize_doc_entry(entry: SecDocRssEntry) -> str:
    return json.dumps(asdict(entry), default=_serialize_datetime)


def _serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
