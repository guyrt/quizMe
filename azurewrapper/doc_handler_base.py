import os
from azure.storage.blob import BlobServiceClient

class AzureBlobHandlerBase:

    container_name = "BLAH"

    def __init__(self):
        self.connection_string = os.environ['DocumentBlobConnectionString']
        self.container_name = os.environ[self.container_name]
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

    def get_path(self, remote_path) -> str:
        blob_stream = self.container_client.download_blob(remote_path)
        return blob_stream.readall().decode('utf-8', 'ignore')
