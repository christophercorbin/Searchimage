from datetime import datetime, timezone

class FaceVectorScore():
    def __init__(self, user_img_store_id, www_img_store_id, face_vector_id, algorithm, score, created_at=None, updated_at=None):
        self.user_img_store_id = user_img_store_id
        self.www_img_store_id = www_img_store_id
        self.face_vector_id = face_vector_id
        self.algorithm = algorithm
        self.score = score
        self.created_at = created_at if created_at is not None else datetime.now(timezone.utc).isoformat()
        self.updated_at = updated_at if updated_at is not None else datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "userImgStoreId": self.user_img_store_id,
            "wwwImgStoreId": self.www_img_store_id,
            "faceVectorId": self.face_vector_id,
            "algorithm": self.algorithm,
            "score": self.score,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        return FaceVectorScore(
            user_img_store_id=data.get('userImgStoreId'),
            www_img_store_id=data.get('wwwImgStoreId'),
            face_vector_id=data.get('faceVectorId'),
            algorithm=data.get('algorithm'),
            score=data.get('score'),
            created_at=data.get('createdAt'),
            updated_at=data.get('updatedAt')
        )