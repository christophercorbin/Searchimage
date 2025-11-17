from config import Config
import unittest
from data.scan_dto import ScanDTO
from data.scan_request_dto import ScanRequestDTO
from bson import ObjectId

class TestUserServiceIntegration(unittest.TestCase):
    def setUp(self):
        self.config = Config.get('dev')

        from services.user_service import UserService
        from clients.db import DbClient
        from repositories.storage_s3_repo import StorageS3Repo

        self.storage_s3_repo = StorageS3Repo()
        self.db_client = DbClient()
        self.user_service = UserService(self.db_client.get_client(), self.storage_s3_repo)

    def test_process_user_images_by_adding_an_existing_user_avatar(self):
        # mock scan request dto
        mock_scan_id = ObjectId()
        user_avatars = ['https://api-dev.protexxa.com/v1/register/ad8628c1-c150-40af-aefe-a059161bfe19/original/avatar.jpeg']
        scan_request_dto = ScanRequestDTO.from_dict({
            'scanId': str(mock_scan_id),
            'clientId': None,
            'userId': 'ad8628c1-c150-40af-aefe-a059161bfe19',
            'addresses': [],
            'names': [],
            'emails': [],
            'webDomains': [],
            'phones': [],
            'companies': [],
            'images': user_avatars
        })
        
        # mock scan dto
        scan_dto = ScanDTO(scan_request_dto)
        
        # get user images
        user_image_faces = self.user_service._get_user_image_faces(scan_dto.client_id, scan_dto.user_id)
        user_images_count = len(user_image_faces)
        self.assertTrue(user_images_count > 0)
        
        # process user images
        self.user_service.process_user_images(user_avatars, scan_dto)
        user_image_faces = self.user_service._get_user_image_faces(scan_dto.client_id, scan_dto.user_id)
        user_images_count_after_processing = len(user_image_faces)

        # assert that the user images count is the same after processing
        print(f'user_images_count: {user_images_count} vs user_images_count_after_processing: {user_images_count_after_processing}')
        self.assertTrue(user_images_count_after_processing == user_images_count)

        # for protexxa platform users, the clientId could be "" or "protexxa", test the case when "protexxa" is use and no more user image is created from the same avatar provided
        scan_request_dto = ScanRequestDTO.from_dict({
            'scanId': str(mock_scan_id),
            'clientId': 'protexxa',
            'userId': 'ad8628c1-c150-40af-aefe-a059161bfe19',
            'addresses': [],
            'names': [],
            'emails': [],
            'webDomains': [],
            'phones': [],
            'companies': [],
            'images': user_avatars
        })

        # process user images
        self.user_service.process_user_images(user_avatars, scan_dto)
        user_image_faces = self.user_service._get_user_image_faces(scan_dto.client_id, scan_dto.user_id)
        user_images_count_after_processing_with_protexxa_as_clientid = len(user_image_faces)

        # assert that the user images count is the same after processing
        print(f'user_images_count: {user_images_count} vs user_images_count_after_processing_with_protexxa_as_clientid: {user_images_count_after_processing_with_protexxa_as_clientid}')
        self.assertTrue(user_images_count_after_processing_with_protexxa_as_clientid == user_images_count)
