from azurewrapper.parsed_doc_handler import AzureParsedDocsBlobHandler
from azurewrapper.raw_doc_handler import AzureSECRawDocsBlobHandler
from azurewrapper.raw_doc_queue import UnderstandDocQueue
from azurewrapper.doc_summary_handler import DocSummaryBlobHandler
from intelligence.doc_understanding_driver import DocUnderstandingDriver



raw_doc = AzureSECRawDocsBlobHandler()
out_qm = UnderstandDocQueue()
parsed_doc = AzureParsedDocsBlobHandler()
doc_summary = DocSummaryBlobHandler()

d = DocUnderstandingDriver(raw_doc, out_qm, parsed_doc, doc_summary)
while True:
    d.run_from_queue()

#for line in d.run_local("samples\jwn-20230729_clean.htm", '10-q'):
for line in d.run_local("samples/karx_10k_clean.htm", '10-q'):
    print(line.prompt.name)
    print(line.response)
