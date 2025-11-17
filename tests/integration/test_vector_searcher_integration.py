import unittest
from config import Config
from data.scan_dto import UserImageFace
from data.search_result import SearchResult
from data.face_match_dto import FaceMatchDto
from data.face_vector_dto import FaceVectorDto
import json


class TestVectorSearcher(unittest.TestCase):
    def setUp(self):
        self.configs = Config.get('dev')

        from repositories.opensearch_repo import OpenSearchRepo
        from services.vector_searcher import VectorSearcher
        from repositories.user_image_repo import UserImageRepo
        from clients.db import DbClient

        open_search_repo = OpenSearchRepo()
        self.vector_searcher = VectorSearcher(open_search_repo)
        self.user_image_repo = UserImageRepo(DbClient().get_client(), self.configs.DB_NAME, self.configs.USER_IMAGE_REPO_NAME)

        # Get the user image from Db
        # {userId:'d2c4a2e6-6144-4e19-94ce-f0dea1159933'} on dev (copied from prod)
        self.test_user_image_entities = self.user_image_repo.get_by_client_user_id('protexxa', 'd2c4a2e6-6144-4e19-94ce-f0dea1159933')

    # skip, tested in test_search_by_test_user
    @unittest.skip('skip')
    def test_search_vectors_by_test_user(self):
        # There should be one user image from DB
        self.assertEqual(len(self.test_user_image_entities), 1)

        uie = self.test_user_image_entities[0]
        
        similar_vectors = self.vector_searcher._search_vectors([UserImageFace(uie.img_store_id, uie.face_vector)])

        print(f'### similar_vectors ({len(similar_vectors)}): {json.dumps([sv.to_dict() for sv in similar_vectors], indent=2)}')

        # Verify that the search result contains the test user's images
        self.assertTrue(len(similar_vectors) > 0)

    def test_search_by_test_user(self):
        # Test searchResult already contains an item from the same site
        existing_search_result = SearchResult('https://www.zoominfo.com/p/Claudette-Mcgowan/1249085421', 'some-title', 'zoominfo.com', [])
        existing_search_result.matched_faces.append(FaceMatchDto('some-storage-id', FaceVectorDto('https://storage.zoominfo.com/-186593231', 'some-img-store-id', 'some-face-store-id', 'some-title', 'https://www.zoominfo.com/p/Claudette-Mcgowan/1249085421', 0.007, 'bbFF_IsBolBgCi9_p34H')))
        
        uie = self.test_user_image_entities[0]
        srs = self.vector_searcher.search([existing_search_result], [UserImageFace(uie.img_store_id, uie.face_vector)])

        print(f'### srs ({len(srs)}): {json.dumps([sr.to_dict() for sr in srs], indent=2)}')
        
        # Test no duplicate site url in search results
        for s in srs:
            self.assertTrue(len([sr for sr in srs if sr.url == s.url]) == 1)

            # Test no duplicate image url in matched faces
            for mf in s.matched_faces:
                self.assertTrue(len([m for m in s.matched_faces if m.matched_face_vector.img_src_url == mf.matched_face_vector.img_src_url]) == 1)

            
        
