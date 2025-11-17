from typing import List
from data.scan_entity import ScanEntity
from data.scan_request_dto import ScanRequestDTO
from services.util_service import UtilService

class UserImageFace():
    def __init__(self, store_id: str, face_vector: List[float]):
        self.store_id = store_id
        self.face_vector = face_vector

    def to_dict(self):
        return {
            'store_id': self.store_id,
            'face_vector': list(self.face_vector)
        }
    
    def to_json(self):
        # Convert the object to a JSON-serializable dictionary
        return {
            "store_id": self.store_id,
            "face_vector": list(self.face_vector)  # Convert to list if it's not
        }
    
    @staticmethod
    def from_dict(dict):
        return UserImageFace(dict['store_id'], dict['face_vector'])

class ScanDTO():
    def __init__(self, request: ScanRequestDTO):
        self.request = request
        self.scan_id = self.request.scan_id
        self.client_id = self.request.client_id
        self.user_id = self.request.user_id
        if len(self.request.addresses) > 0:
            self.in_country = UtilService.get_user_country_code(request.addresses[0].to_dict()).lower()
        else:
            # get default country code
            self.in_country = UtilService.get_user_country_code('').lower()
        self.user_images_local_dir = f'temp/{self.scan_id}' # temporary directory to store user images provided in the scan request
        self.user_image_faces:List[UserImageFace] = [] # list of user face information extracted from the user images

    @staticmethod
    def from_scan_entity(entity:ScanEntity):
        return ScanDTO(entity.scan_id, entity.client_id, entity.user_id)
    
    @staticmethod
    def from_dict(dict):
        request = ScanRequestDTO.from_dict(dict['request'])
        print(f'### from request: {request}')
        scan = ScanDTO(request)
        scan.user_images_local_dir = dict['user_images_local_dir']
        scan.user_image_faces = [UserImageFace.from_dict(f) for f in dict['user_image_faces']]
        
        return scan
    
    def to_dict(self):
        return {
            'scan_id': self.scan_id,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'in_country': self.in_country,
            'location_code': self.location_code,
            'user_images_local_dir': self.user_images_local_dir,
            'user_image_faces': [f.to_dict() for f in self.user_image_faces],
            'request': self.request.to_dict()
        }
        
