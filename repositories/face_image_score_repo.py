from pymongo import MongoClient
from data.face_image_score_entity import FaceImageScoreEntity
from config import Config
import logging

class FaceImageScoreRepo():
    def __init__(self, db_client: MongoClient, db_name, collection_name):
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_FACE_IMAGE_SCORE_REPO)
        self._client = db_client
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]

    def add(self, face_image_score_entity: FaceImageScoreEntity) -> str:
        """
        Adds a new face image score to the database

        :param face_image_score_entity: the face image score to add
        :returns: the id of the inserted face image score
        """
        # Convert the FaceImageScoreEntity to a dict before insertion
        result = self._collection.insert_one(face_image_score_entity.to_dict())
        return result.inserted_id
    
    def add_many(self, face_image_score_entities: list[FaceImageScoreEntity]) -> list[str]:
        """
        Adds a list of new face image scores to the database

        :param face_image_score_entities: the list of face image scores to add
        :returns: the ids of the inserted face image scores
        """
        # Convert the FaceImageScoreEntity to a dict before insertion
        result = self._collection.insert_many([face_image_score_entity.to_dict() for face_image_score_entity in face_image_score_entities])
        return result.inserted_ids
