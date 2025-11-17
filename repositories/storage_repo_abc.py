from abc import ABC, abstractmethod
from data.image_type_enum import ImageTypeEnum

class StorageRepoABC(ABC):
    @abstractmethod
    def add_image(self, type:ImageTypeEnum, dst_file_path, src_file_path):
        pass

    @abstractmethod
    def rename_image(self, type:ImageTypeEnum, dst_file_path, src_file_path):
        pass

    @abstractmethod
    def remove(self, type:ImageTypeEnum, dst_file_path):
        pass

    @abstractmethod
    def get_source_user_image(self, key, dst_dir):
        pass

    @abstractmethod
    def get_storage_by_type(self, type:ImageTypeEnum) -> str:
        pass