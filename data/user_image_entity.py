from datetime import datetime, timezone
from typing import List

class UserImageEntity():
    def __init__(self, img_url, img_store_id, face_vector:List[float], scan_id='', client_id='', user_id='', 
                 agg_face_vector:List[float]=[], agg_face_vector_ids=[], created_at=None, updated_at=None):
        # for scans without a user, client & user Ids will be empty
        # for scans with a user, client & user Ids will be populated, scan_id will be empty
        # a user can have multiple entries, each for a different image uploaded. 
        # if the same profile picture is provided for a user on a new scan, it will not be stored into storage, and thus, the storageID will be the same from the matching image from a previous scan
        self.img_url = img_url
        self.img_store_id = img_store_id
        self.face_vector = face_vector
        if len(agg_face_vector) > 0:
            self.agg_face_vector = agg_face_vector
        else:
            # initialize the aggregate face vector to the initial face vector
            self.agg_face_vector = self.face_vector
        self.agg_face_vector_ids = agg_face_vector_ids
        self.scan_id = scan_id
        self.client_id = client_id
        self.user_id = user_id
        self.created_at = created_at if created_at is not None else datetime.now(timezone.utc).isoformat()
        self.updated_at = updated_at if updated_at is not None else datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            'imgUrl': self.img_url,
            'imgStoreId': self.img_store_id,
            'faceVector': self.face_vector,
            'aggFaceVector': self.agg_face_vector,
            'aggFaceVectorIds': self.agg_face_vector_ids,
            'scanId': self.scan_id,
            'clientId': self.client_id,
            'userId': self.user_id,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }
    
    @staticmethod
    def from_dict(dict):
        return UserImageEntity(
            dict['imgUrl'],
            dict['imgStoreId'],
            dict['faceVector'],
            dict['scanId'],
            dict['clientId'],
            dict['userId'],
            dict['aggFaceVector'],
            dict['aggFaceVectorIds'],
            dict['createdAt'],
            dict['updatedAt']
        )
    



