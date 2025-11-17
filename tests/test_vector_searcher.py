import unittest
from services.vector_searcher import VectorSearcher
from data.face_vector_dto import FaceVectorDto
from data.search_result import SearchResult
from data.scan_dto import UserImageFace

class TestVectorSearcher(unittest.TestCase):
    def test_search_new_result(self):
        '''
        This is a unit test for the search method in the VectorSearcher class.
        It tests the case when there are no search results and the search method is called.
        '''
        # mock the VectorDbRepoABC
        class VectorDbRepoABC:
            def search(self, v, num, min_score):
                return [FaceVectorDto('img_url', 'img_str_id', 'face_str_id', 'site_title', 'site_url', 0.9, 'v_id')]
            
        vector_db = VectorDbRepoABC()
        search_results = []
        vs = VectorSearcher(vector_db)
        results = vs.search(search_results, [UserImageFace('store_id', [1.23, 4.56, 7.89])])
        self.assertEqual(len(results), 1)

    def test_search_add_to_existing_search_result(self):
        '''
        This is a unit test for the search method in the VectorSearcher class.
        It tests the case when there is an existing search result and the search method is called.
        '''
        # mock the VectorDbRepoABC
        class VectorDbRepoABC:
            def search(self, v, num, min_score):
                return [FaceVectorDto('img_url', 'img_str_id', 'face_str_id', 'site_title', 'site_url', 0.9, 'v_id')]
            
        vector_db = VectorDbRepoABC()
        search_results = [SearchResult('site_url', 'site_title', 'site_url', [])]
        vs = VectorSearcher(vector_db)
        results = vs.search(search_results, [UserImageFace('store_id', [1.23, 4.56, 7.89])])
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0].matched_faces), 1)
            