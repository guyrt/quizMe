import os
from azure.storage.queue import QueueServiceClient, QueueMessage


class AzureQueueManager:
    def __init__(self):
        self.connection_string = os.environ['DocumentBlobConnectionString']
        self.queue_name = os.environ['DocumentRawProcessQueueName']
        self.extract_table_queue_name = os.environ['DocumentRawExtractStructuredDataQueueName']
        queue_service_client = QueueServiceClient.from_connection_string(self.connection_string)
        self.queue_client = queue_service_client.get_queue_client(self.queue_name)
        self.extract_table_q_client = queue_service_client.get_queue_client(self.extract_table_queue_name)

    def write_message(self, message):
        self.queue_client.send_message(message)
        self.extract_table_q_client.send_message(message)

    def pop_doc_parse_message(self, peek=True) -> QueueMessage:
        """Assume that the upstream system will requeue if this message is a problem."""
        if peek:
            msg = self.queue_client.peek_messages(1)[0]
        else:
            msg = self.queue_client.receive_message(1, visibility_timeout=120)

        if msg:
            return msg
        
    def delete_doc_parse_message(self, msg : QueueMessage):
        self.queue_client.delete_message(msg)
