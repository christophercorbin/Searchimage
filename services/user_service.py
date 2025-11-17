from typing import List
from data.user_leak_dto import UserLeakDto
from data.face_match_dto import FaceMatchDto
from data.search_result import SearchResult
from data.web_image_entity import WebImageEntity
from data.user_image_entity import UserImageEntity
from data.scan_dto import ScanDTO, UserImageFace
from data.image_type_enum import ImageTypeEnum
from repositories.leak_repo import LeakRepo
from repositories.web_image_repo import WebImageRepo
from repositories.user_image_repo import UserImageRepo
from repositories.storage_repo_abc import StorageRepoABC
from repositories.vector_db_repo_abc import VectorDbRepoABC
from config import Config
from bson.objectid import ObjectId
from pymongo import MongoClient
from services.util_service import UtilService
from services.image_processor import ImageProcessor
import logging
import os
import re

class UserService():
    def __init__(self, db_client: MongoClient, storage_client: StorageRepoABC):
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_USER_SERVICE)
        self._leaks_repo = LeakRepo(db_client, self._configs.DB_NAME, self._configs.LEAK_REPO_NAME)
        self._user_image_repo = UserImageRepo(db_client, self._configs.DB_NAME, self._configs.USER_IMAGE_REPO_NAME)
        self._web_image_repo = WebImageRepo(db_client, self._configs.DB_NAME, self._configs.WEB_IMAGE_REPO_NAME)
        self._image_processor = ImageProcessor(storage_client, self._web_image_repo)
        self._storage = storage_client
        

    def _get_user_leaks(self, client_id, user_id) -> List[UserLeakDto]:
        user_leaks: List[UserLeakDto] = []

        # Get all leaks that are associated with the user (ignore client_id for now as it could be either None (or "protexxa") for defender users)
        leaks = self._leaks_repo.get_all_by_user_id(user_id)
        # leaks = self._leaks_repo.get_all_by_client_user_ids(client_id, user_id)
        if leaks is None or len(leaks) == 0:
            return None   

        # Get all images that are associated with each leak
        for leak in leaks:
            if not leak.leaks or not leak.leaks.img_doc_ids or len(leak.leaks.img_doc_ids) == 0:
                continue
            web_images = self._web_image_repo.get_all_by_ids(leak.leaks.img_doc_ids)
            user_leaks.append(UserLeakDto(leak, web_images))
        
        return user_leaks
    
    def _download_user_image(self, img_url, dst_dir):
        """
        Helper method to download user image from img_url
        """
        # save user profile picture to temporary directory
        user_img_path = ''
        if not img_url:
            return user_img_path

        # build s3_key from user's profile picture link that starts with 'register'
        match = re.search(r'register/.+', img_url)
        s3_key = match.group() if match else None
        if s3_key:
            user_img_path = self._storage.get_source_user_image(s3_key, dst_dir)
        else:
            # reversed for test user whose image urls most likely don't contain register/
            user_img_path = UtilService.download_user_image(img_url, dst_dir)
        
        return user_img_path

    
    def _get_user_image_faces(self, client_id, user_id) -> List[UserImageFace]:
        if not user_id:
            # only check user_id as client_id could be None for internal clients
            return []
        
        user_images = self._user_image_repo.get_by_client_user_id(client_id, user_id)

        # tranform user images to user image faces
        user_image_faces = []
        for user_image in user_images:
            user_image_faces.append(UserImageFace(user_image.img_store_id, user_image.face_vector))

        return user_image_faces

    
    def process_user_images(self, img_urls, scan_dto: ScanDTO):
        """
        For each provided user image:
        - Download image from img_urls
        - Save image to remote storage
        - Embed image into face vectors
        - Check if the user image already exists in db
        - If not, store the first image embedding into db
        - Add image embedding to scan_dto for similarity calculation with images from the web (storeId) later

        Args:
            img_urls: List[str] - list of user image urls
            scan_dto: ScanDTO - scan data transfer object, also the output of this method that stores the user image faces
        """
        user_image_faces = self._get_user_image_faces(scan_dto.client_id, scan_dto.user_id)
        if len(user_image_faces) > 0:
            # add user image faces from previous scans to scan_dto
            scan_dto.user_image_faces = user_image_faces

        for i, img_url in enumerate(img_urls):
            img_path = self._download_user_image(img_url, scan_dto.user_images_local_dir)
            if not img_path:
                continue
            
            # save image to remote storage
            filepath, ext = os.path.splitext(img_path)
            storage_id = f'{scan_dto.scan_id}-{i}{ext}'
            res = self._storage.add_image(ImageTypeEnum.USER, storage_id, img_path)

            # embed image into face vector
            face_dict = None
            try: 
                face_dicts = self._image_processor.embed_image(self._storage.get_storage_by_type(ImageTypeEnum.USER), storage_id)
                if not face_dicts:
                    # short circuit here and try the user's next image
                    continue

                face_numbers = len(face_dicts)
                if face_numbers == 0:
                    self._logger.error(f'In scan: {scan_dto.scan_id}, no face ({face_numbers}) detected in {storage_id}, will not process this user image')
                    continue
                elif face_numbers > 1:
                    # if there is more than one face in user image, use the largest one
                    face_dict = max(face_dicts, key=lambda item: item['facial_area']['w'] * item['facial_area']['h'])
                    self._logger.warn(f"In scan: {scan_dto.scan_id}, invalid number of faces ({face_numbers}) detected in {storage_id}, will process the largest face: {face_dict['facial_area']['w']} * {face_dict['facial_area']['h']}")
                else:
                    # this is the expected behavior where there is only one face in user image
                    face_dict = face_dicts[0]
            except Exception as e:
                self._logger.error(f'In scan: {scan_dto.scan_id}, failed to embed user image from {storage_id} into face vectors: {e}')
                # short circuit here and try the user's next image
                continue

            if not face_dict.get('embedding'):
                self._logger.error(f'In scan: {scan_dto.scan_id}, failed to embed user image from {storage_id} with invalid result: {face_dict}')
                # short circuit here and try the user's next image
                continue

            # If user image(s) exists from previous scans, calculate similarity with previous images, only save new ones
            user_image_existed = False
            if len(scan_dto.user_image_faces) > 0:
                for uif in scan_dto.user_image_faces:
                    distance = UtilService.find_cosine_distance(uif.face_vector, face_dict['embedding'])
                    if distance < self._configs.MAX_MACTHING_SIMILARITY_DISTANCE:
                        # the new user image provided is considered the same as an existing one from previous scan, skip it
                        user_image_existed = True
                        break

            if not user_image_existed:
                # Create a new user image record and add it to the db
                user_image = UserImageEntity(img_url, storage_id, face_dict['embedding'], scan_id=scan_dto.scan_id, client_id=scan_dto.client_id, user_id=scan_dto.user_id)
                self._user_image_repo.add(user_image)

                # Add the new user face embedding to scan_dto to calculate similarity with images from the web later
                scan_dto.user_image_faces.append(UserImageFace(storage_id, face_dict['embedding']))

    
    def filter_search_results(self, client_id, user_id, search_results:List[SearchResult]) -> List[SearchResult]:
        '''
        If a user leak contains a site url also found in the search results
            - update the user leak record with any new matched vectors found in the search result
              by updating the web images in the user leaks
            - remove the search result so we don't need to process it again

        Args:
            client_id: str
            user_id: str
            search_results: List[SearchResult]

        Returns:
            List[SearchResult]
        '''
        user_leaks = self._get_user_leaks(client_id, user_id)
        if user_leaks is None:
            return search_results
        
        for user_leak in user_leaks:
            for search_result in search_results:
                if user_leak.site_url == search_result.url:
                    # update the user leak record with any new matched vectors found in the search result of a site
                    ids = self._update_site_user_web_images_found(user_leak, search_result.matched_faces)
                    
                    # add the new web images to the user leak
                    if len(ids) > 0:
                        user_leak.leak_image_ids.extend(ids)
                        self._leaks_repo.update_image_ids_by_id(user_leak.leak_id, user_leak.leak_image_ids)

                    # remove the search result since the user leak already contains it
                    search_results.remove(search_result)
                    # break - do not break here as there might be multiple search results for the same site

        return search_results
    
    def _update_site_user_web_images_found(self, user_leak: UserLeakDto, matched_faces: List[FaceMatchDto]) -> List[ObjectId]:
        '''
        On a website, the user already had some leaks found. We also found some matched vectors on the same website.
        See if the matched vectors are also found in the user leaks. If not, add them to the user leaks.

        Args:
            user_leaks: UserLeakDto - the user leaks found on the websites
            matched_vectors: List[FaceVectorDto] - the matched vectors found on the website

        Returns:
            List[ObjectId] - the ids of the new web images created to be added to the user leaks images
        '''
        user_leak_images = user_leak.web_images
        new_web_images: List[WebImageEntity] = []

        for mf in matched_faces:
            mfv = mf.matched_face_vector
            if mfv and mfv.img_src_url not in [img.src_url for img in user_leak_images]:
                # create a new web image record and add it to the user leak
                new_web_image = WebImageEntity(mf.matched_face_vector.site_url, mf.matched_face_vector.img_src_url, mf.matched_face_vector.img_storage_id, 
                                               mf.src_face_storage_id, mf.matched_face_vector.doc_id, 'vdb', mf.matched_face_vector.score)
                new_web_images.append(new_web_image)

        if len(new_web_images) > 0:
            return self._web_image_repo.add_many(new_web_images)
        
        return []


        

