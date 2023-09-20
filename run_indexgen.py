from azurewrapper.raw_doc_handler import AzureRawDocsBlobHandler
from azurewrapper.raw_doc_queue import ProcessRawDocQueue

from indexgen.zip_handler import FileCopyDriver

from dotenv import load_dotenv

load_dotenv()

uploader = AzureRawDocsBlobHandler()
driver = FileCopyDriver(uploader, ProcessRawDocQueue())
driver.run_local("C:/Users/riguy/Downloads/sec.gov_Archives_edgar_monthly_xbrlrss-2023-08.xml", "https://www.sec.gov/Archives/edgar/data/1920145/000119312523209095/0001193125-23-209095-xbrl.zip")
#driver.download_extract_upload()
