import unittest
from services.event_handler import EventHandler
from data.scan_dto import ScanDTO
from data.scan_entity import ScanEntity
from data.address import Address
from data.scan_request_dto import ScanRequestDTO
from repositories.scan_repo import ScanRepo
from config import Config
import json

class TestEventHandler(unittest.TestCase):
    def setUp(self):
        self._configs = Config.get()
        self._event_handler = EventHandler()
        self._scan_repo = ScanRepo(self._event_handler._db_client, self._configs.DB_NAME, self._configs.SCAN_REPO_NAME)      

    def test_process(self):
        '''
        This is an integration test that tests the entire flow of the app
        '''
        # mock address
        address1 = Address.from_dict({
            'street': 'West Fireweed Lane',
            'number': '121',
            'city': 'Anchorage',
            'postalCode': '12345',
            'country': 'US'
        })

        # create a scan request
        request = ScanRequestDTO.from_dict({
            'scanId': '789',
            'clientId': '456',
            'userId': '789',
            'names': ['Mary Sattler Peltola'],
            'companies': ['U.S. REPRESENTATIVE'],
            'images': ['https://peltola.house.gov/uploadedphotos/highresolution/56440a66-676c-41c0-8767-8b7bc549ac6d.jpg']
        })

        # this onees worked
        # request = ScanRequestDTO.from_dict({
        #     'scanId': '789',
        #     'clientId': '456',
        #     'userId': '789',
        #     'addresses': [address1.to_dict()],
        #     'names': ['Mary Sattler Peltola', 'Mary Peltola'],
        #     'emails': ['team@marypeltola.com'],
        #     'webDomains': [],
        #     'phones': ['(907) 921-6575', '225-5765'],
        #     'companies': ['U.S. REPRESENTATIVE'],
        #     # 'images': ['https://peltola.house.gov/uploadedphotos/highresolution/56440a66-676c-41c0-8767-8b7bc549ac6d.jpg']
        # })

        # request = ScanRequestDTO.from_dict({
        #     'scanId': '123',
        #     'clientId': '456',
        #     'userId': '789',
        #     'addresses': [],
        #     # 'names': ['Mary Sattler Peltola'],
        #     'emails': ['team@marypeltola.com'],
        #     'webDomains': [],
        #     'phones': ['(907) 921-6575'],
        #     'companies': [],
        #     'images': []
        # })

        # with this request, the scan is stuck... at spider closed
        # request = ScanRequestDTO.from_dict({
        #     'scanId': '123',
        #     'clientId': '456',
        #     'userId': '789',
        #     'addresses': [address1.to_dict()],
        #     'names': ['Mary Sattler Peltola'],
        #     'emails': [],
        #     'webDomains': [],
        #     'phones': ['225-5765'],
        #     'companies': ['U.S. REPRESENTATIVE'],
        #     'images': ['https://peltola.house.gov/uploadedphotos/highresolution/56440a66-676c-41c0-8767-8b7bc549ac6d.jpg']
        # })

        # mock scan dto
        scan_dto = ScanDTO(request)

        # mock scan entity
        scan_entity = ScanEntity(
            scan_id=scan_dto.scan_id,
            client_id=scan_dto.client_id,
            user_id=scan_dto.user_id,
            payload=request.to_dict()
        )

        scan = self._scan_repo.get_by_scan_id(scan_dto.scan_id)
        # insert the scan entity into DB if it doesn't exist from previous tests
        if scan is None:
            self._scan_repo.add(scan_entity)

        # process the scan - the business logic of the app
        self._event_handler.process(json.dumps(request.to_dict()))

        # get the scan from DB
        scan = self._scan_repo.get_by_scan_id(scan_dto.scan_id)
        print(f'### scan: {scan}')
        self.assertEqual(scan.status, 'processing')




