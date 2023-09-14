from azurewrapper.raw_doc_handler import AzureRawDocsBlobHandler
from azurewrapper.raw_doc_queue import ProcessRawDocQueue

from indexgen.zip_handler import FileCopyDriver

from dotenv import load_dotenv

load_dotenv()

uploader = AzureRawDocsBlobHandler()
driver = FileCopyDriver(uploader, ProcessRawDocQueue())
driver.download_extract_upload()
