from data.user_image_entity import UserImageEntity
from pymongo import MongoClient
from pymongo.collection import ReturnDocument
from config import Config
from typing import List
import logging

class UserImageRepo():
    def __init__(self, db_client: MongoClient, db_name, collection_name) -> None:
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_USER_IMAGE_REPO)
        self._client = db_client
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]

    def add(self, user_image:UserImageEntity):
        # Convert the UserImageEntity to a dict before insertion
        result = self._collection.insert_one(user_image.to_dict())
        return result.inserted_id
    
    def get_by_client_user_id(self, client_id, user_id) -> List[UserImageEntity]:
        query = {'userId': user_id}

        # when client id is either empty or protexxa, the user is by default a protexxa platform user, no need to search by client id
        # otherwise, we use clientId in the query to prevent userId collisions
        if client_id and client_id != 'protexxa':
            query['clientId'] = client_id

        results = self._collection.find(query)

        return [UserImageEntity.from_dict(result) for result in results]