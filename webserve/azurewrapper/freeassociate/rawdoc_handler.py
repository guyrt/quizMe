from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

from django.conf import settings
from users.models import User
from users.key_manager import EncryptionWrapper

class EncryptedDocHandlerBase:

    def __init__(self, connection_string, container_name=None):
        self.connection_string = connection_string
        self.container_name = container_name

        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

        self._encryption_wrapper = EncryptionWrapper()

    def upload(self, user : User, input : str, timestamp : str, filename : str):
        full_filename = f"{user.pk}/{timestamp}/{filename}"
        blob_client = self.container_client.get_blob_client(full_filename)
        encrypted_content = self._encryption_wrapper.encrypt(user, input)
        blob_client.upload_blob(encrypted_content, overwrite=True)  # todo return and store etags
        return self.container_name, full_filename

    def download(self, user : User, remote_path):
        try:
            raw_blob_stream = self.container_client.download_blob(remote_path)
        except ResourceNotFoundError:
            raise ValueError(f"Failure to find blob {remote_path}")

        return self._encryption_wrapper.decrypt(user, raw_blob_stream.readall())

    def walk_blobs(self, prefix : str, blob_name : str):
        for blob in self.container_client.list_blobs(name_starts_with=prefix):
            if blob.name.endswith(blob_name):
                yield blob.name


class RawDocCaptureHander(EncryptedDocHandlerBase):

    def __init__(self, container_name=None):
        connection_string = settings.AZURE['FA_RAWDOCS']['CONNECTION']
        container_name = container_name or settings.AZURE['FA_RAWDOCS']['CONTAINER']
        super().__init__(connection_string, container_name)


class ProcessedDocCaptureHander(EncryptedDocHandlerBase):

    def __init__(self, container_name=None):
        connection_string = settings.AZURE['FA_PROCESSEDDOCS']['CONNECTION']
        container_name = container_name or settings.AZURE['FA_PROCESSEDDOCS']['CONTAINER']
        super().__init__(connection_string, container_name)
