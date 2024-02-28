import os
from azure.storage.queue import QueueServiceClient, QueueMessage

import dotenv

dotenv.load_dotenv()


class AzureQueueManagerBase:
    queue_name = "fake"

    def __init__(self):
        self.connection_string = os.environ["DocumentBlobConnectionString"]
        self.queue_name = self.queue_name

        self._queue_service_client = QueueServiceClient.from_connection_string(
            self.connection_string
        )

        self._queue_client = self._queue_service_client.get_queue_client(
            self.queue_name
        )
        self._error_queue_client = None

    def write_message(self, message):
        self._queue_client.send_message(message)

    def write_error(self, message):
        if self._error_queue_client is None:
            self._error_queue_client = self._queue_service_client.get_queue_client(
                f"{self.queue_name}-error"
            )
        self._error_queue_client.send_message(message)

    def pop_doc_parse_message(self, peek=True) -> QueueMessage:
        """Assume that the upstream system will requeue if this message is a problem."""
        if peek:
            msg = self._queue_client.peek_messages(1)[0]
        else:
            msg = self._queue_client.receive_message(visibility_timeout=120)

        if msg:
            return msg
        else:
            raise ValueError("no work to do")

    def delete_doc_parse_message(self, msg: QueueMessage):
        self._queue_client.delete_message(msg)


class ProcessRawDocQueue(AzureQueueManagerBase):
    queue_name = os.environ["DocumentRawProcessQueueName"]


class UnderstandDocQueue(AzureQueueManagerBase):
    queue_name = os.environ["ParsedDocumentProcessQueueName"]
