from repositories.storage_repo_abc import StorageRepoABC
from repositories.web_image_repo import WebImageRepo
from data.image_type_enum import ImageTypeEnum
from config import Config
import logging
import boto3
import hashlib
import json
import os
from PIL import Image

class InvalidImageError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class ImageProcessor():
    def __init__(self, storage_repo: StorageRepoABC, web_image_repo: WebImageRepo):
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_IMAGE_PROCESSOR)
        self._storage_repo = storage_repo
        self._web_image_repo = web_image_repo

        # Initialize the SageMaker client
        self._image_analyzer = boto3.client('sagemaker-runtime', 'us-east-1')
        self._image_analyzer_endpoint = self._configs.IMAGE_INFERENCE_ENDPOINT_QUICK
        self._image_analyzer_content_type = "application/json"

    def generate_image_storage_id(self, img_url, ext) -> str:
        """
        Generates a unique key for the provided image url

        :param img_url: the url of the image
        :param ext: the extension of the image
        :returns: the storage key of the image
        """
        return hashlib.md5(img_url.encode('utf-8')).hexdigest() + ext

    def upload_image(self, img_path, img_storage_id, img_type: ImageTypeEnum) -> str:
        """
        Uploads the provided image to remote storage

        :param img_path: path to where the image is stored locally
        :param img_storage_id: the id used to store the image in a remote storage
        :returns: the storage key of the uploaded image
        :raises InvalidImageError: if the provided image is invalid
        """
        self._storage_repo.add_image(img_type, img_storage_id, img_path)
        return img_storage_id

    def embed_image(self, img_storage='', img_storage_id=''):
        """
        Embeds the specified image in a remote storage (only S3 bucket supported for now) to face vector(s)

        :param img_storage: the storage where the image is stored
        :param img_storage_id: the id of the image in the storage
        :returns: array of dict (faces) containing embedding and facial_area from each face in the image
        :raises InvalidImageError: if the provided image is invalid
        """
        # Make the inference request to embed the image
        payload = {
            "bucket": img_storage,
            "key": img_storage_id
        }

        response = self._image_analyzer.invoke_endpoint(
            EndpointName=self._image_analyzer_endpoint,
            ContentType=self._image_analyzer_content_type,
            Body=json.dumps(payload).encode('utf-8')
        )

        # Decode the result
        result = json.loads(response['Body'].read().decode())
        if 'error' in result:
            raise InvalidImageError(f'Error embedding image from: {img_storage}:{img_storage_id}, error: {result}')
        
        return result
    
    def crop_face_from_image(self, src_img_path, facial_area, face_idx=0) -> str:
        x = facial_area["x"]
        y = facial_area["y"]
        w = facial_area["w"]
        h = facial_area["h"]

        with Image.open(src_img_path) as img:
            img_cropped = img.crop((x, y, x + w, y + h))
        
            # Convert the image mode to RGB to remove alpha channel
            img_cropped = img_cropped.convert('RGB')

            # Save the cropped image
            base_path, ext = os.path.splitext(src_img_path)
            user_face_path = f"{base_path}-face{face_idx}{ext}"
            try:
                img_cropped.save(user_face_path)
            except Exception as e:
                self._logger.error(f'Failed to save cropped image: {user_face_path}, error: {e}')
                raise e

            return user_face_path

    def embed_images(self, images):
        vectors = []
        for image in images:
            vectors.append(self.embed(image))
        return vectors

