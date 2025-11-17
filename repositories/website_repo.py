from typing import List
from data.website_entity import WebsiteEntity
from pymongo import MongoClient
from bson.objectid import ObjectId

class WebsiteRepo():
    def __init__(self, db_client: MongoClient, db_name, collection_name):
        self._client = db_client
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]

    def add(self, website_entity: WebsiteEntity) -> str:
        """
        Adds a new website to the database

        :param website_entity: the website to add
        :returns: the id of the inserted website
        """
        # Convert the WebsiteEntity to a dict before insertion
        result = self._collection.insert_one(website_entity.to_dict())
        return result.inserted_id
    
    def get(self, website_id: str) -> WebsiteEntity:
        """
        Gets a website from the database

        :param website_id: the id of the website to get
        :returns: the website with the given id
        """
        website = self._collection.find_one({"_id": ObjectId(website_id)})
        return WebsiteEntity.from_dict(website)
    
    def get_by_url(self, url: str) -> WebsiteEntity:
        """
        Gets a website from the database

        :param url: the url of the website to get
        :returns: the website with the given url
        """
        website = self._collection.find_one({"url": url})
        return WebsiteEntity.from_dict(website)
    