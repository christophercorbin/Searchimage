import unittest
from data.scan_request_dto import ScanRequestDTO
import json

class TestScanRequestDTO(unittest.TestCase):
    def test_from_json_happy_path(self):
        request = '{"scanId": "123", "clientId": "456"}'
        dto = ScanRequestDTO.from_dict(json.loads(request))

        self.assertEqual(dto.scan_id, "123")
        self.assertEqual(dto.client_id, "456")
