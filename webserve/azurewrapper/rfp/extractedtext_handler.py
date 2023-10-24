from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from webserve.privateuploads.models import DocFormat


class RfpExtractedTextBlobHander:

    def __init__(self, container_name=None):
        self.connection_string = settings.AZURE['RFP_EXTRACTEDTEXT']['CONNECTION']
        self.container_name = container_name or settings.AZURE['RFP_EXTRACTEDTEXT']['CONTAINER']

        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

    def upload(self, input : str, filename : str):
        blob_client = self.container_client.get_blob_client(filename)
        blob_client.upload_blob(input, overwrite=True)  # todo return and store etags
        return self.container_name, filename

    def get_path(self, remote_path):
        try:
            blob_stream = self.container_client.download_blob(remote_path)
        except ResourceNotFoundError:
            raise ValueError(f"Failure to find blob {remote_path}")

        return blob_stream.readall().decode('utf-8', 'ignore')

    def walk_blobs(self, prefix : str, blob_name : str):
        for blob in self.container_client.list_blobs(name_starts_with=prefix):
            if blob.name.endswith(blob_name):
                yield blob.name
