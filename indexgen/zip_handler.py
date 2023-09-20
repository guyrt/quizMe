import requests
import zipfile
import io
import tempfile
import os

from azurewrapper.raw_doc_handler import AzureRawDocsBlobHandler

from .common import headers
from azurewrapper.gate import Gate
from .read_rss import get_all_entries, get_local_entries


class FileCopyDriver(object):

    def __init__(self, uploader : AzureRawDocsBlobHandler, doc_queue) -> None:
        self._doc_uploader = uploader
        self._raw_doc_queue = doc_queue

    def download_extract_upload(self):
        with Gate(2) as g:  # 10 per sec is SEC max.
            for row in get_all_entries():
                self._handle_row(row, g)

    def run_local(self, path, after=None):
        skip = (after is not None)

        with Gate(1) as g:
            for row in get_local_entries(path):
                if skip and row.zip_link == after:
                    skip = False
                    import pdb; pdb.set_trace()
                if not skip:
                    self._handle_row(row, g)

    def _handle_row(self, row, gate):
        
        if self._doc_uploader.exists(row):
            return
        
        gate.gate()

        url = row.zip_link
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise AttributeError(f"Hit {r.status_code} downloading {url}")

        z = zipfile.ZipFile(io.BytesIO(r.content))
        with tempfile.TemporaryDirectory() as temp_dir:
            z.extractall(temp_dir)

            filehandles = {}

            # note: these are actually flat. We assume so in our filehandles.
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    full_filename = os.path.join(root, file)
                    filehandles[file] = full_filename

            summary_path = self._doc_uploader.upload_files(row, filehandles)
            self._raw_doc_queue.write_message(summary_path)

        print(f"Processed {row.cik}: {row.id}")
