from datetime import datetime, timezone
from bson.objectid import ObjectId

class FaceImageScoreEntity():
    def __init__(self, user_img_store_id, www_img_src_url, www_img_store_id, www_face_vector_id, www_face_store_id, algorithm, score, _id=None):
        self._id = _id if _id else ObjectId()
        self.user_img_store_id = user_img_store_id
        self.www_img_src_url = www_img_src_url
        self.www_img_store_id = www_img_store_id
        self.www_face_vector_id = www_face_vector_id
        self.www_face_store_id = www_face_store_id
        self.algorithm = algorithm
        self.score = score
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            '_id': self._id,
            'userImgStoreId': self.user_img_store_id,
            'wwwImgSrcUrl': self.www_img_src_url,
            'wwwImgStoreId': self.www_img_store_id,
            'wwwFaceVectorId': self.www_face_vector_id,
            'wwwFaceStoreId': self.www_face_store_id,
            'algorithm': self.algorithm,
            'score': self.score,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }
    
    @staticmethod
    def from_dict(obj):
        return FaceImageScoreEntity(
            obj['_id'],
            obj['userImgStoreId'],
            obj['wwwImgSrcUrl'],
            obj['wwwImgStoreId'],
            obj['wwwFaceVectorId'],
            obj['wwwFaceStoreId'],
            obj['algorithm'],
            obj['score']
        )