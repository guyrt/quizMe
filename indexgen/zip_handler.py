import requests
import zipfile
import io
import tempfile
import os

from .common import headers
from .gate import Gate
from .read_rss import get_all_entries, SecDocRssEntry


class FileCopyDriver(object):

    def __init__(self, uploader, queue) -> None:
        self._doc_uploader = uploader
        self._raw_doc_queue = queue

    def download_extract_upload(self):
        with Gate(2) as g:  # 10 per sec is SEC max.
            for row in get_all_entries():
                g.gate()
                # TODO - check if we have it

                url = row.zip_link
                r = requests.get(url, headers=headers)
                if r.status_code != 200:
                    raise AttributeError(f"Hit {r.status_code} downloading {url}")
                    # todo eat this.

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


def classify_files(entry : SecDocRssEntry):
    main_file = None
    other_files = []
    for file_obj in entry.edgar_files:
        file_type = file_obj.filetype
        if file_type and (not file_type.startswith('EX')):
            main_file = file_obj
        else:
            other_files.append(file_obj)
    return {'main': main_file, 'other': other_files}

