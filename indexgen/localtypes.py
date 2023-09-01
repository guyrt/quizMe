from dataclasses import dataclass
from datetime import datetime

from typing import List

@dataclass(slots=True)
class EdgarFile:
    filename : str
    filetype : str
    url : str


@dataclass(slots=True)
class SecDocRssEntry:
    doc_type: str  # 8-k ect
    title : str
    zip_link : str
    published : datetime
    id : str   # usually the file name.
    cik : str
    edgar_files : List[EdgarFile]    
    company_name : str
    edgar_assistantdirector : str
