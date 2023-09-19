
from typing import List
from writer.writer_types import KnownFact


class Tool:

    name = "name"
    description = "dummy"

    # TODO: always must log a query and a source that comes back from tool.
    # This is how we'll track provenance.

    def run(self, query)-> List[KnownFact]:
        #raise NotImplementedError()
        return []
