from azurewrapper.parsed_doc_handler import AzureParsedDocsBlobHandler
from azurewrapper.raw_doc_handler import AzureRawDocsBlobHandler
from azurewrapper.raw_doc_queue import UnderstandDocQueue
from azurewrapper.doc_summary_handler import DocSummaryBlobHandler
from intelligence.doc_understanding_driver import DocUnderstandingDriver



raw_doc = AzureRawDocsBlobHandler()
out_qm = UnderstandDocQueue()
parsed_doc = AzureParsedDocsBlobHandler()
doc_summary = DocSummaryBlobHandler()

d = DocUnderstandingDriver(raw_doc, out_qm, parsed_doc, doc_summary)
d.run_from_queue()
d.run_local("C:/tmp/clean.html", '8-k')
