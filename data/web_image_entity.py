
from datetime import datetime, timezone
from typing import List
import uuid
from bson.objectid import ObjectId

class WebImageEntity():
    def __init__(self, site_url, src_url, web_img_store_id, user_img_store_id, face_vector_id, algorithm, score, 
                 state="PENDING", created_at=None, updated_at=None, _id:ObjectId = None):
        self._id = _id if _id else ObjectId()
        self.site_url = site_url
        self.src_url = src_url
        self.web_img_store_id = web_img_store_id
        self.user_img_store_id = user_img_store_id
        self.algorithm = algorithm
        self.score = score
        self.state = state
        self.face_vector_id = face_vector_id # the id of the face vector that matched an user face
        self.created_at = created_at if created_at is not None else datetime.now(timezone.utc).isoformat()
        self.updated_at = updated_at if updated_at is not None else datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "siteUrl": self.site_url,
            "srcUrl": self.src_url,
            "webImgStoreId": self.web_img_store_id,
            "userImgStoreId": self.user_img_store_id,
            "algorithm": self.algorithm,
            "score": self.score,
            "state": self.state,
            "faceVectorId": self.face_vector_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        return WebImageEntity(
            _id=data.get('_id'),
            site_url=data.get('siteUrl'),
            src_url=data.get('srcUrl'),
            web_img_store_id=data.get('webImgStoreId'),
            user_img_store_id=data.get('userImgStoreId'),
            algorithm=data.get('algorithm'),
            score=data.get('score'),
            state=data.get('state'),
            face_vector_id=data.get('faceVectorId'),
            created_at=data.get('createdAt'),
            updated_at=data.get('updatedAt')
        )
