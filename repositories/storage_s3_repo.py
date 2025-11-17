'''
PYTHONPATH=$PYTHONPATH:/home/ec2-user/defender-be-image-reverse-search:/home/ec2-user/defender-be-image-reverse-search/repositories
export PYTHONPATH
'''
import boto3
import logging
import os
from config import Config
from repositories.storage_repo_abc import StorageRepoABC
from data.image_type_enum import ImageTypeEnum

class StorageS3Repo(StorageRepoABC):
    def __init__(self):
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_IMAGE_STORAGE_REPO)
        self._bucket_user_images = self._configs.USER_IMAGE_STORAGE_BUCKET_NAME # used by DME to store provided user images from scan request
        self._bucket_user_images_source = self._configs.USER_PROFILE_SOURCE_STORAGE_BUCKET_NAME # provided by internal client (Protexxa) - which is used by the client to store user images 
        self._bucket_web_images = self._configs.WEB_IMAGE_STORAGE_BUCKET_NAME

        # Get the service resource.
        self._client = boto3.resource('s3')

    def add_image(self, type:ImageTypeEnum, dst_file_path, src_file_path):
        bucket = self._bucket_web_images
        if type == ImageTypeEnum.USER:
            bucket = self._bucket_user_images

        try:
            with open(src_file_path, 'rb') as src_file:
                return self._client.Object(bucket, dst_file_path).put(Body=src_file)
        except Exception as e:
            self._logger.error(f'adding: {src_file_path} to storage failed with error: {e}')
            raise e
        
        return None

    def rename_image(self, type:ImageTypeEnum, dst_file_path, src_file_path):
        bucket = self._bucket_web_images
        if type == ImageTypeEnum.USER:
            bucket = self._bucket_user_images

        try:
            self._client.Object(bucket, dst_file_path).copy_from(CopySource=f'{bucket}/{src_file_path}')
            self._client.Object(bucket, src_file_path).delete()
        except Exception as e:
            self._logger.error(f'renaming from: {src_file_path} to {dst_file_path} failed with error: {e}')
            raise e
        
    def remove(self, type:ImageTypeEnum, dst_file_path):
        bucket = self._bucket_web_images
        if type == ImageTypeEnum.USER:
            bucket = self._bucket_user_images

        try:
            self._client.Object(bucket, dst_file_path).delete()
        except Exception as e:
            self._logger.error(f'removing: {dst_file_path} from storage failed with error: {e}')
            raise e
        
    def get_source_user_image(self, key, dst_dir):
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        try:
            dst_img_path = os.path.join(dst_dir, os.path.basename(key))

            bucket = self._client.Bucket(self._bucket_user_images_source)
            obj = bucket.Object(key)
            obj.download_file(dst_img_path)
            self._logger.debug(f'got: {key} to {dst_img_path}')

            return dst_img_path
        except Exception as e:
            self._logger.error(f'getting: {key} from storage failed with error: {e}')
            return ''
        
    def get_storage_by_type(self, type:ImageTypeEnum) -> str:
        if type == ImageTypeEnum.USER:
            return self._bucket_user_images
        else:
            return self._bucket_web_images

if __name__ == '__main__':
    storage = StorageS3Repo()
    # storage.add('trudeau3.jpg', '/home/ec2-user/defender-be-image-reverse-search/test/assets/Justin Trudeau/trudeau-3ppl.jpg')
    storage.get_source_user_image('register/04285e03-b4b6-4d3d-bb76-bfed33f669c8/original/avatar.webp', '')