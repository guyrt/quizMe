import os

from .doc_handler_base import AzureBlobHandlerBase

class DocSummaryBlobHandler(AzureBlobHandlerBase):

    container_name = 'ParsedDocumentBlobContainer'

    def upload_files(self, original_doc_path : str, content : str):

        remote_path = os.path.dirname(original_doc_path)
        full_path = f'{remote_path}/summaries.jsonl'

        blob_client = self.container_client.get_blob_client(full_path)
        if blob_client.exists():
            blob_client.append_block(content, len(content))
        else:
            blob_client.upload_blob(content)
