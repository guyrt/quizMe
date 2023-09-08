import os

from .doc_handler_base import AzureBlobHandlerBase

class DocSummaryBlobHandler(AzureBlobHandlerBase):

    container_name = 'ParsedDocumentBlobContainer'

    def upload_files(self, original_doc_path : str, content : str):

        remote_path = os.path.dirname(original_doc_path)

        blob_client = self.container_client.get_blob_client(remote_path)
        blob_client.append_block(content, len(content))
