import os
from azure.storage.queue import QueueServiceClient

from dotenv import load_dotenv

load_dotenv()


class AzureQueueWriter:
    def __init__(self):
        self.connection_string = os.environ['DocumentBlobConnectionString']
        self.queue_name = os.environ['DocumentQueueName']
        queue_service_client = QueueServiceClient.from_connection_string(self.connection_string)
        self.queue_client = queue_service_client.get_queue_client(self.queue_name)

    def write_message(self, message):
        self.queue_client.send_message(message)
