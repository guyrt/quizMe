import os
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

import dotenv

dotenv.load_dotenv()


class AzureBlobHandlerBase:
    container_name = "BLAH"

    def __init__(self):
        self.connection_string = os.environ["DocumentBlobConnectionString"]
        self.container_name = os.environ[self.container_name]
        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

    def get_path(self, remote_path) -> str:
        try:
            blob_stream = self.container_client.download_blob(remote_path)
        except ResourceNotFoundError:
            raise ValueError(f"Failure to find blob {remote_path}")

        return blob_stream.readall().decode("utf-8", "ignore")

    def walk_blobs(self, prefix: str, blob_name: str):
        for blob in self.container_client.list_blobs(name_starts_with=prefix):
            if blob.name.endswith(blob_name):
                yield blob.name
