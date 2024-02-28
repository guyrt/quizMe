from io import BytesIO

from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceNotFoundError

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from privateuploads.types import DocFormat, docformat_to_contenttype


class KMRawBlobHander:
    def __init__(self, container_name=None):
        self.connection_string = settings.AZURE["KM_RAW_BLOB"]["CONNECTION"]
        self.container_name = (
            container_name or settings.AZURE["KM_RAW_BLOB"]["CONTAINER"]
        )

        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

    def upload(
        self, inmem_file: InMemoryUploadedFile, filename: str, data_type: DocFormat
    ):
        blob_client = self.container_client.get_blob_client(filename)

        content_str = docformat_to_contenttype(data_type)
        content_settings = ContentSettings(content_type=content_str)

        blob_client.upload_blob(
            inmem_file, overwrite=True, content_settings=content_settings
        )  # todo return and store etags
        inmem_file.seek(0)
        return self.container_name, filename

    def get_path_to_bytes(self, remote_path) -> BytesIO:
        try:
            blob_stream = self.container_client.download_blob(remote_path)
        except ResourceNotFoundError:
            raise ValueError(f"Failure to find blob {remote_path}")

        stream = BytesIO()
        blob_stream.readinto(stream)
        return stream

    def walk_blobs(self, prefix: str, blob_name: str):
        for blob in self.container_client.list_blobs(name_starts_with=prefix):
            if blob.name.endswith(blob_name):
                yield blob.name
