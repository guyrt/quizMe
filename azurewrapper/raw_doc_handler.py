import os
from azure.storage.blob import BlobServiceClient
from datetime import datetime
from typing import Dict

from indexgen.localtypes import SecDocRssEntry, serialize_doc_entry

class AzureRawDocsBlobHandler:
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
        summary_path = os.path.join(root, "summary.json")
        blob_client = self.container_client.get_blob_client(summary_path)
        blob_client.upload_blob(serialize_doc_entry(sec_entry), overwrite=True)
        return summary_path
    
    def get_path(self, remote_path) -> str:
        blob_stream = self.container_client.download_blob(remote_path)
        blob_stream.readall().decode('utf-8', 'ignore')

    def _build_root_path(self, sec_entry : SecDocRssEntry):
        # todo check if exists. roll counter if so.
        return f"{sec_entry.cik}/{datetime.strftime(sec_entry.published, '%Y%m%d')}/{sec_entry.doc_type}_0"
