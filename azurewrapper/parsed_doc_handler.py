from azure.storage.blob import BlobPrefix

from .doc_handler_base import AzureBlobHandlerBase
from docparsers.docparsertypes import ParsedDoc, serialized_parsed_doc

class AzureParsedDocsBlobHandler(AzureBlobHandlerBase):

    container_name = "ParsedDocumentBlobContainer"

    def upload_files(self, parsed_doc : ParsedDoc, content : str):

        remote_path = parsed_doc.doc_id
        remote_details_path = f'{parsed_doc.doc_id}.details.json'

        blob_client = self.container_client.get_blob_client(remote_path)
        blob_client.upload_blob(content, overwrite=True)

        blob_client = self.container_client.get_blob_client(remote_details_path)
        blob_client.upload_blob(serialized_parsed_doc(parsed_doc), overwrite=True)

    def walk_blobs(self, prefix : str, blob_name : str):
        for blob in self.container_client.list_blobs(name_starts_with=prefix):
            if blob.name.endswith(blob_name):
                yield blob.name
