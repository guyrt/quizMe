from azurewrapper.raw_doc_handler import AzureRawDocsBlobHandler
from azurewrapper.raw_doc_queue import ProcessRawDocQueue

from indexgen.zip_handler import FileCopyDriver

from dotenv import load_dotenv

load_dotenv()

uploader = AzureRawDocsBlobHandler()
driver = FileCopyDriver(uploader, ProcessRawDocQueue())
driver.run_local("C:/Users/riguy/Downloads/xbrlrss-2023-04.xml", "https://www.sec.gov/Archives/edgar/data/1949594/000119312523106459/0001193125-23-106459-xbrl.zip")
#driver.download_extract_upload()
