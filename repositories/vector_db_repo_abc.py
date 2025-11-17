from abc import ABC, abstractmethod
from typing import List
from data.face_vector_dto import FaceVectorDto

class VectorDbRepoABC(ABC):
    @abstractmethod
    def search(self, vector, num=7, min_score=0.01) -> List[FaceVectorDto]:
        """
        Search for (num, number of) user images that have a good chance of containing 
        the user's face by the face vector
        """
        pass

    @abstractmethod
    def search_by_url(self, url):
        pass

    @abstractmethod
    def image_processed(self, url) -> bool:
        """
        Check in the db if any index contains the url. If there is, that means the image
        pointed by the url has been processed before
        """
        pass

    @abstractmethod
    def insert(self, vector, img_src_url, img_s3_key, site_url='', site_title='', face_s3_key=''):
        pass