from azurewrapper.cosmos_sec_facts import CosmosDbSecFactsHander
from azurewrapper.raw_doc_handler import AzureRawDocsBlobHandler
from azurewrapper.raw_doc_queue import ProcessRawDocQueue, UnderstandDocQueue
from azurewrapper.parsed_doc_handler import AzureParsedDocsBlobHandler

from docparsers.driver import ParserDriver
from docparsers.structured_data_upload import StructuredDataHandler

from dotenv import load_dotenv

load_dotenv()

raw_doc = AzureRawDocsBlobHandler()
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

# content, data = driver.parse_local_file("samples/jwn-20230729.htm", "10-k")
# fh = open("samples/jwn-20230729_clean.htm", "w", encoding='utf-8')
# fh.write(content)

while True:
    driver.parse_from_queue()
