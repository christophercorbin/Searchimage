from pymongo import MongoClient
from bson.objectid import ObjectId
from data.web_image_entity import WebImageEntity
from config import Config
import logging
from typing import List

class WebImageRepo():
    def __init__(self, db_client: MongoClient, db_name, collection_name):
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_WEB_IMAGE_REPO)
        self._client = db_client
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]

    def add(self, web_image_entity: WebImageEntity) -> ObjectId:
        """
        Adds a new web image to the database

        :param web_image_entity: the web image to add
        :returns: the id of the inserted web image
        """
        # Convert the WebImageEntity to a dict before insertion
        result = self._collection.insert_one(web_image_entity.to_dict())
        return result.inserted_id
    
    def add_many(self, web_images: List[WebImageEntity]) -> List[ObjectId]:
        """
        Adds new web images to the database

        :param web_images: the web images to add
        :returns: the ids of the inserted web images
        """
        # Convert the WebImageEntity to a dict before insertion
        result = self._collection.insert_many([wi.to_dict() for wi in web_images])
        return result.inserted_ids
    
    def get_all_by_ids(self, ids: List[ObjectId]) -> List[WebImageEntity]:
        """
        Gets all web images by ids

        :param ids: the ids of the web images
        :returns: a list of web images
        """
        web_images = []
        for web_image in self._collection.find({'_id': {'$in': ids}}):
            web_images.append(WebImageEntity.from_dict(web_image))
        return web_images
    