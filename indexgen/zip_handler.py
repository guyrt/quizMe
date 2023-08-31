import requests
import zipfile
import io
import tempfile
import os
from common import headers
from gate import Gate

from read_rss import get_all_entries, SecDocRssEntry


def download_extract():
    with Gate(10) as g:  # 10 per sec is SEC max.
        for row in get_all_entries():
            # todo - check if we have it

            url = row.zip_link
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                raise AttributeError(f"Hit {r.status_code} downloading {url}")
                # todo eat this.

            print(classify_files(row))

            z = zipfile.ZipFile(io.BytesIO(r.content))
            with tempfile.TemporaryDirectory() as temp_dir:
                z.extractall(temp_dir)
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        full_filename = os.path.join(root, file)
                        print(full_filename)

            import ipdb; ipdb.set_trace()
                        # with open(full_filename, 'r') as f:
                        #     print(f.read())
            g.gate()


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


if __name__ == "__main__":
    download_extract()

