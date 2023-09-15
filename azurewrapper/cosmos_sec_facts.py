import os

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

import dotenv
dotenv.load_dotenv()


class CosmosDbSecFactsHander:

    def __init__(self) -> None:
        self._container_name = os.environ['SecFactsStoreContainer']
        self._database_name = os.environ['SecFactsStoreDatabase']
        endpoint = os.environ['SecFactsStoreEndpoint']
        key = os.environ['SecFactsStoreKey']
        self._client = CosmosClient(endpoint, key)

        self._database = self._client.create_database_if_not_exists(id=self._database_name)
        self._container = self._database.create_container_if_not_exists(id=self._container_name, partition_key="/cik")

    def write(self, obj):
        try:
            existing_item = self._container.read_item(obj['id'], partition_key=obj['cik'])
        except CosmosHttpResponseError:
            # it didn't exist
            self._container.create_item(obj)
        else:
            # upsert if newer
            if existing_item['docdate'] < obj['docdate']:
                self._container.upsert_item(obj)
