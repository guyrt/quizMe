import requests
import zipfile
import io
import tempfile
import os
from common import headers
from gate import Gate
import json

from read_rss import get_all_entries, SecDocRssEntry

def download_extract():
    with Gate(1) as g:  # 10 per sec is SEC max.
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
                        
                        #with open(full_filename, 'r') as f:
                        #    print(f.read())
            g.gate()


def classify_files(entry : SecDocRssEntry):
    main_file = None
    other_files = []
    for file_obj in json.loads(entry.xbrl_json_str):
        import ipdb; ipdb.set_trace()
        file_type = file_obj.get('edgar_type')
        if file_type and (not file_type.starts_with('EX')):
            main_file = file_obj['edgar_url']
        else:
            other_files.append(file_obj['edgar_url'])
    return {'main': main_file, 'other': other_files}


if __name__ == "__main__":
    download_extract()

