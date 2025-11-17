from typing import List
from data.address import Address
from data.site_image_dto import SiteImageDTO
from bson.objectid import ObjectId
from data.web_image_entity import WebImageEntity
from data.leak_entity import LeakEntity

class UserLeakDto:
    def __init__(self, leak: LeakEntity, web_images: List[WebImageEntity] = []) -> None:
        self.leak_id = leak._id
        self.leak_image_ids = leak.leaks.img_doc_ids
        self.site_url = leak.url
        self.web_images = web_images

    def to_dict(self):
        return {
            'leak_id': self.leak_id,
            'site_url': self.site_url,
            'web_images': [wi.to_dict() for wi in self.web_images]
        }