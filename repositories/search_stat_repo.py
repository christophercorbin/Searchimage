from pymongo import MongoClient
from config import Config
import logging
from typing import List
from data.search_stat_entity import SearchStatEntity

class SearchStatRepo():
    def __init__(self, db_client: MongoClient, db_name, collection_name):
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_SEARCH_STAT_REPO)
        self._client = db_client
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]

    def add(self, search_stat_entity: SearchStatEntity) -> str:
        """
        Adds a new search stat to the database

        :param search_stat_entity: the search stat to add
        :returns: the id of the inserted search stat
        """
        # Convert the SearchStatEntity to a dict before insertion
        result = self._collection.insert_one(search_stat_entity.to_dict())
        return result.inserted_id