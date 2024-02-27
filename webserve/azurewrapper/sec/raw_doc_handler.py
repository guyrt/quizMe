import os
from datetime import datetime
from typing import Dict

from parser_utils.indexgen.localtypes import SecDocRssEntry, serialize_doc_entry
from ..doc_handler_base import AzureBlobHandlerBase


class AzureSECRawDocsBlobHandler(AzureBlobHandlerBase):
    container_name = "RawDocumentBlobContainer"

    def exists(self, sec_entry: SecDocRssEntry):
        root = self._build_root_path(sec_entry)
        summary_path = os.path.join(root, "summary.json")
        blob_client = self.container_client.get_blob_client(summary_path)
        return blob_client.exists()

    def upload_files(self, sec_entry: SecDocRssEntry, local_files: Dict[str, str]):
        root = self._build_root_path(sec_entry)

        for filename, localpath in local_files.items():
            blob_client = self.container_client.get_blob_client(
                os.path.join(root, filename)
            )
            with open(localpath, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

        # Summary
        summary_path = os.path.join(root, "summary.json")
        blob_client = self.container_client.get_blob_client(summary_path)
        blob_client.upload_blob(serialize_doc_entry(sec_entry), overwrite=True)
        return summary_path

    def _build_root_path(self, sec_entry: SecDocRssEntry):
        # TODO check if exists. roll counter if so.
        while True:
            path = f"{sec_entry.cik}/{datetime.strftime(sec_entry.published, '%Y%m%d')}/{sec_entry.doc_type}_0"

            return path
