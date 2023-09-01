import os
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from datetime import datetime
from dataclasses import asdict
import json
from typing import Dict

from dotenv import load_dotenv
from localtypes import SecDocRssEntry

load_dotenv()

class AzureBlobUploader:
    def __init__(self):
        self.connection_string = os.environ['DocumentBlobConnectionString']
        self.container_name = os.environ['DocumentBlobContainer']
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

    def upload_files(self, sec_entry : SecDocRssEntry, local_files : Dict[str, str]):
        root = self._build_root_path(sec_entry)

        for filename, localpath in local_files.items():
            blob_client = self.container_client.get_blob_client(os.path.join(root, filename))
            with open(localpath, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

        # Summary
        summary_content = json.dumps(asdict(sec_entry), default=serialize_datetime)
        blob_client = self.container_client.get_blob_client(os.path.join(root, "summary.json"))
        blob_client.upload_blob(summary_content, overwrite=True)


    def _build_root_path(self, sec_entry : SecDocRssEntry):
        # todo check if exists. roll counter if so.
        return f"{sec_entry.cik}/{datetime.strftime(sec_entry.published, '%Y%m%d')}/{sec_entry.doc_type}_0"
    

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')