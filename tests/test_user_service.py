import unittest
from services.user_service import UserService
from repositories.leak_repo import LeakRepo
from repositories.web_image_repo import WebImageRepo
from config import Config
from pymongo import MongoClient
from data.user_leak_dto import UserLeakDto
from data.search_result import SearchResult
from data.face_match_dto import FaceMatchDto
from data.face_vector_dto import FaceVectorDto
from data.leak_entity import LeakEntity, Leak
from data.web_image_entity import WebImageEntity
from bson.objectid import ObjectId
from typing import List

class TestUserService(unittest.TestCase):
    def setUp(self):
        self._configs = Config.get()
        self._db_client = MongoClient(self._configs.DB_URL)
        self._user_service = UserService(self._db_client)

    def test_filter_search_results_no_existing_leaks(self):
        '''
        This is a unit test for the filter_search_results method in the user service
        Test the case where the user has no leaks found in search results
        the search results should not be modified
        '''
        sr_1 = SearchResult('https://www.example.com', 'hello', 'example.com', ['www.example.com/face1.jpg', 'www.example.com/face2.jpg'])
        sr_2 = SearchResult('https://www.example2.com', 'world', 'example2.com', ['www.example2.com/face1.jpg', 'www.example2.com/face2.jpg'])
        sr_1.matched_faces = [FaceMatchDto('mock-user-profile-strorage-id', 
                                FaceVectorDto('www.example.com/face1.jpg', 'mock-strorage-id', 'mock-face-strorage-id', 'mock-site-title', 'https://www.example.com', 0.5, 'mock-doc-id'))]
        sr_2.matched_faces = [FaceMatchDto('mock-user-profile-strorage-id', 
                                FaceVectorDto('www.example2.com/face1.jpg', 'mock-strorage-id', 'mock-face-strorage-id', 'mock-site-title', 'https://www.example2.com', 0.5, 'mock-doc-id'))]
        search_results = [sr_1, sr_2]

        # mock user has no leaks
        self._user_service._get_user_leaks = lambda client_id, user_id: None

        filtered_search_results = self._user_service.filter_search_results('client-id', 'user-id', search_results)

        self.assertEqual(len(filtered_search_results), 2)
        self.assertEqual(filtered_search_results[0].url, 'https://www.example.com')
        self.assertEqual(filtered_search_results[1].url, 'https://www.example2.com')


    def test_filter_search_results_with_existing_leaks_and_matching_web_images(self):
        '''
        This is a unit test for the filter_search_results method in the user service
        Test the case where the user has a leak from a site that's also found in the search results
        and the leak record has a web image from previous scan which also matches the web image from search results
        the search result should be removed from the search results
        '''
        sr_1 = SearchResult('https://www.example.com', 'hello', 'example.com', ['www.example.com/face1.jpg', 'www.example.com/face2.jpg'])
        sr_2 = SearchResult('https://www.example2.com', 'world', 'example2.com', ['www.example2.com/face1.jpg', 'www.example2.com/face2.jpg'])
        sr_1.matched_faces = [FaceMatchDto('mock-user-profile-strorage-id', 
                                FaceVectorDto('www.example.com/face1.jpg', 'mock-strorage-id1', 'mock-face-strorage-id1', 'mock-site-title1', 'https://www.example.com', 0.5, 'mock-doc-id1'))]
        sr_2.matched_faces = [FaceMatchDto('mock-user-profile-strorage-id', 
                                FaceVectorDto('www.example2.com/face1.jpg', 'mock-strorage-id2', 'mock-face-strorage-id2', 'mock-site-title2', 'https://www.example2.com', 0.5, 'mock-doc-id2'))]
        search_results = [sr_1, sr_2]

        user_leak = UserLeakDto(LeakEntity('hello', 'https://www.example.com', 
                                           leak=Leak(img_doc_ids=[ObjectId('123456781234567812345678')])), 
                                            [WebImageEntity('https://www.example.com', 'www.example.com/face1.jpg', 'mock-strorage-id1', 'mock-doc-id1', _id=ObjectId('123456781234567812345678'))])
        self._user_service._get_user_leaks = lambda client_id, user_id: [user_leak]

        # mock the update site user web images found method - it should add any new web images to the user leak since the user leak already has web image from search results
        self._user_service._update_site_user_web_images_found = lambda user_leak, matched_faces: []

        filtered_search_results = self._user_service.filter_search_results('client-id', 'user-id', search_results)

        self.assertEqual(len(filtered_search_results), 1)
        self.assertEqual(filtered_search_results[0].url, 'https://www.example2.com')


    def test_filter_search_results_with_existing_leaks_but_no_matching_web_images(self):
        '''
        This is a unit test for the filter_search_results method in the user service
        Test the case where the user has a leak from a site that's also found in the search results
        but the leak record has no web images from previous scan
        the web image from search results should be added to the leak record
        the item will be removed from search results 
        '''
        sr_1 = SearchResult('https://www.example.com', 'hello', 'example.com', ['www.example.com/face1.jpg', 'www.example.com/face2.jpg'])
        sr_2 = SearchResult('https://www.example2.com', 'world', 'example2.com', ['www.example2.com/face1.jpg', 'www.example2.com/face2.jpg'])
        sr_1.matched_faces = [FaceMatchDto('mock-user-profile-strorage-id', 
                                FaceVectorDto('www.example.com/face1.jpg', 'mock-strorage-id1', 'mock-face-strorage-id1', 'mock-site-title1', 'https://www.example.com', 0.5, 'mock-doc-id1'))]
        sr_2.matched_faces = [FaceMatchDto('mock-user-profile-strorage-id', 
                                FaceVectorDto('www.example2.com/face1.jpg', 'mock-strorage-id2', 'mock-face-strorage-id2', 'mock-site-title2', 'https://www.example2.com', 0.5, 'mock-doc-id2'))]
        search_results = [sr_1, sr_2]

        user_leak = UserLeakDto(LeakEntity('hello', 'https://www.example.com', 
                                           leak=Leak()), 
                                            [])
        self._user_service._get_user_leaks = lambda client_id, user_id: [user_leak]

        # mock the update site user web images found method - it should add any new web images to the user leak since the user leak already has web image from search results
        self._user_service._update_site_user_web_images_found = lambda user_leak, matched_faces: [ObjectId('123456781234567812345678')]

        # mock update image ids by id method
        self._user_service._leaks_repo.update_image_ids_by_id = lambda leak_id, img_ids: None

        filtered_search_results = self._user_service.filter_search_results('client-id', 'user-id', search_results)

        self.assertEqual(len(filtered_search_results), 1)
        self.assertEqual(filtered_search_results[0].url, 'https://www.example2.com')
        self.assertEqual(user_leak.leak_image_ids, [ObjectId('123456781234567812345678')])
        

    def test_update_site_user_web_images_add_new_web_image(self):
        '''
        This is a unit test for the _update_site_user_web_images_found method in the user service
        It should create the web image found in the search result into the user's leaks on the same site if it doesn't contain the web image already
        '''
        new_web_img_id = ObjectId('123456781234567812345678')
        user_leak = UserLeakDto(LeakEntity('hello', 'https://www.example.com', leak=Leak()))
        matched_faces = [FaceMatchDto('mock-user-profile-strorage-id', 
                                FaceVectorDto('www.example.com/face1.jpg', 'mock-strorage-id1', 'mock-face-strorage-id1', 'mock-site-title1', 'https://www.example.com', 0.5, 'mock-doc-id1'))]
        
        # mock add many mehod into face image score repo
        self._user_service._face_image_score_repo.add_many = lambda face_image_scores: None

        # mock add many method in web image repo
        self._user_service._web_image_repo.add_many = lambda web_images: list([new_web_img_id])

        new_web_image_ids = self._user_service._update_site_user_web_images_found(user_leak, matched_faces)

        self.assertEqual(new_web_image_ids, [new_web_img_id])
