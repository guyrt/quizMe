from azurewrapper.raw_doc_handler import AzureRawDocsBlobHandler
from azurewrapper.raw_doc_queue import ProcessRawDocQueue, UnderstandDocQueue
from azurewrapper.parsed_doc_handler import AzureParsedDocsBlobHandler

from docparsers.driver import ParserDriver

from dotenv import load_dotenv

load_dotenv()

raw_doc = AzureRawDocsBlobHandler()
iqm = ProcessRawDocQueue()
out_qm = UnderstandDocQueue()
parsed_doc = AzureParsedDocsBlobHandler()
driver = ParserDriver(raw_doc, iqm, parsed_doc, out_qm)

print(len(driver.parse_local_file("samples/jwn-20230729.htm")))
#while True:
#    driver.parse_from_queue()
