from webserve.azurewrapper.sec.cosmos_sec_facts import CosmosDbSecFactsHander
from webserve.azurewrapper.sec.raw_doc_handler import AzureSECRawDocsBlobHandler
from webserve.azurewrapper.sec.raw_doc_queue import ProcessRawDocQueue, UnderstandDocQueue
from webserve.azurewrapper.sec.parsed_doc_handler import AzureParsedDocsBlobHandler

from webserve.parser_utils.docparsers.driver import ParserDriver
from webserve.parser_utils.docparsers.structured_data_upload import StructuredDataHandler

from dotenv import load_dotenv

load_dotenv()

raw_doc = AzureSECRawDocsBlobHandler()
iqm = ProcessRawDocQueue()
out_qm = UnderstandDocQueue()
parsed_doc = AzureParsedDocsBlobHandler()
structured_data_handler = StructuredDataHandler(CosmosDbSecFactsHander())
driver = ParserDriver(
    raw_doc,
    iqm,
    parsed_doc,
    out_qm,
    structured_data_handler,
    peek_mode=False
)

# fn = "samples/r9523010q"
# content, data = driver.parse_local_file(f"{fn}.htm", "10-k")
# fh = open(f"{fn}_clean.htm", "w", encoding='utf-8')
# fh.write(content)

#while True:
#    driver.parse_from_queue()

driver.parse_from_cik("0000789019")
