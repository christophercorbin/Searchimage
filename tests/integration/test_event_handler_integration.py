import unittest
from services.event_handler import EventHandler
from data.scan_dto import ScanDTO
from data.scan_entity import ScanEntity
from data.address import Address
from data.scan_request_dto import ScanRequestDTO
from repositories.scan_repo import ScanRepo
from config import Config
import json


class TestEventHandlerIntegration(unittest.TestCase):
    def setUp(self):
        self._configs = Config.get()
        self._event_handler = EventHandler()
    

    def mock_request(self):
        return ScanRequestDTO.from_dict({
            'scanId': '123',
            'clientId': '456',
            'userId': '789',
            'names': ['Mary Sattler Peltola'],
            'emails': ['team@marypeltola.com'],
            'webDomains': [],
            'companies': [],
            'images': ['https://peltola.house.gov/uploadedphotos/highresolution/56440a66-676c-41c0-8767-8b7bc549ac6d.jpg']
        })
    

    def test_process(self):
        '''
        This is an integration test to see if the process uses the backup serper in case of main serper failure.
        '''

        # create a scan request
        request = self.mock_request()

        # test case: If the default serper fails, event handler must switch to the backup serper.
        self._event_handler.process(json.dumps(request.to_dict()))
        # Expected results: Finish the process with no errors 

        # test takes about 17s






