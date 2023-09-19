from dataclasses import dataclass, asdict
from typing import List
import json


@dataclass
class Topic:

    name: str
    description : str
    questions : List[str] = None


@dataclass
class Section:

    name : str
    topics : List[Topic]
    


@dataclass
class Plan:
    """A plan is a series of sections. 
    Each section has a list of topics
    Each topic should have a list of factual needs and/or questions.
    """
    sections : List[Section]


def serialize_plan(plan : Plan):
    return json.dumps(asdict(plan))


@dataclass
class KnownFactSource:
    source_type : str  # URL, SEC thing ect.
    value : str


@dataclass
class KnownFactInternal:
    was_useful : bool = None
    query : str = ""
    trigger : str = ""


@dataclass
class KnownFact:
    value : str
    long_value : str
    source : KnownFactSource
    internal : KnownFactInternal