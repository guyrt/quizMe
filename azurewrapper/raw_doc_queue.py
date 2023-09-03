import os
from azure.storage.queue import QueueServiceClient, QueueMessage


class AzureQueueWriter:
    def __init__(self):
        self.connection_string = os.environ['DocumentBlobConnectionString']
        self.queue_name = os.environ['DocumentQueueName']
        queue_service_client = QueueServiceClient.from_connection_string(self.connection_string)
        self.queue_client = queue_service_client.get_queue_client(self.queue_name)

    def write_message(self, message):
        self.queue_client.send_message(message)

    def pop_message(self) -> QueueMessage:
        """Assume that the upstream system will requeue if this message is a problem."""
        msg = self.queue_client.receive_message(visibility_timeout=120)
        if msg:
            return msg
        
    def delete_message(self, msg : QueueMessage):
        self.queue_client.delete_message(msg)
