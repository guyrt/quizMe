from ..doc_handler_base import AzureBlobHandlerBase
from parser_utils.docparsers.docparsertypes import ParsedDoc, serialized_parsed_doc


class AzureParsedDocsBlobHandler(AzureBlobHandlerBase):
    container_name = "ParsedDocumentBlobContainer"

    def upload_files(self, parsed_doc: ParsedDoc, content: str):
        remote_path = parsed_doc.doc_id
        remote_details_path = f"{parsed_doc.doc_id}.details.json"

        blob_client = self.container_client.get_blob_client(remote_path)
        blob_client.upload_blob(content, overwrite=True)

        blob_client = self.container_client.get_blob_client(remote_details_path)
        blob_client.upload_blob(serialized_parsed_doc(parsed_doc), overwrite=True)
