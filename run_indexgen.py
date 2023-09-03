from azurewrapper.raw_doc_handler import AzureRawDocsBlobHandler
from azurewrapper.raw_doc_queue import AzureQueueWriter

from indexgen.zip_handler import FileCopyDriver

from dotenv import load_dotenv

load_dotenv()

uploader = AzureRawDocsBlobHandler()
driver = FileCopyDriver(uploader, AzureQueueWriter())
driver.download_extract_upload()
