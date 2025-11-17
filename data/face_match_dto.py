from typing import List
from data.face_vector_dto import FaceVectorDto

class FaceMatchDto():
    def __init__(self, src_face_storage_id: str, matched_face_vector: FaceVectorDto):
        self.src_face_storage_id = src_face_storage_id # storage id of the user picture provided 
        self.matched_face_vector = matched_face_vector

    def to_dict(self):
        return {
            'src_face_storage_id': self.src_face_storage_id,
            'matched_face_vector': self.matched_face_vector.to_dict()
        }