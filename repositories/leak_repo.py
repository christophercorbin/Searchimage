from pymongo import MongoClient
from data.leak_entity import LeakEntity
from config import Config
import logging
from typing import List
from bson.objectid import ObjectId
from pymongo.collection import ReturnDocument

class LeakRepo():
    def __init__(self, db_client: MongoClient, db_name, collection_name):
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_LEAK_REPO)
        self._client = db_client
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]

    def add(self, leak_entity: LeakEntity) -> str:
        """
        Adds a new leak to the database

        :param leak_entity: the leak to add
        :returns: the id of the inserted leak
        """
        # Convert the LeakEntity to a dict before insertion
        result = self._collection.insert_one(leak_entity.to_dict())
        return result.inserted_id

    def update_image_ids_by_id(self, _id: ObjectId, img_doc_ids: List[ObjectId]) -> LeakEntity:
        """
        Updates the image ids of a leak by id

        :param _id: the id of the leak
        :param img_doc_ids: the image ids to update
        :returns: the updated leak
        """
        # Update the image ids of the leak
        result = self._collection.find_one_and_update(
            {'_id': _id},
            {'$set': {'leaks.imgDocIds': img_doc_ids}},
            return_document=ReturnDocument.AFTER
        )
        return LeakEntity.from_dict(result)
    
    def get_all_by_user_id(self, user_id: str) -> List[LeakEntity]:
        """
        Gets all leaks by user id

        :param user_id: the user id
        :returns: a list of leaks
        """
        filter_query = {'userId': user_id}
        
        try:
            leaks = [LeakEntity.from_dict(leak) for leak in self._collection.find(filter_query)]
        except Exception as e:
            self._logger.error(f"Failed to fetch leaks from database: {e}")
            return []
        return leaks

    def get_all_by_client_user_ids(self, client_id: str, user_id: str) -> List[LeakEntity]:
        """
        Gets all leaks by client and user ids

        :param client_id: the client id
        :param user_id: the user id
        :returns: a list of leaks
        """
        filter_query = {'userId': user_id}
        if client_id:
            filter_query['clientId'] = client_id
        
        try:
            leaks = [LeakEntity.from_dict(leak) for leak in self._collection.find(filter_query)]
        except Exception as e:
            self._logger.error(f"Failed to fetch leaks from database: {e}")
            return []
        return leaks
    