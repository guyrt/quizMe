from dataclasses import dataclass

@dataclass(slots=True)
class ParsedDoc:

    doc_id : str = None  # guid of the doc
    doc_maker : str = None  # string detailing software used to parse.
    parse_date : str = None  # string date when we parsed.

    # todo - store the version (via git?) of the parser you used.

