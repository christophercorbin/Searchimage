import unittest
from data.address import Address
from data.scan_request_dto import ScanRequestDTO
from data.scan_dto import ScanDTO, UserImageFace
from services.web_searcher import WebSearcher

class TestWebSearcherIntegration(unittest.TestCase):
    def mock_address1(self):
        return Address.from_dict({
            'street': 'West Fireweed Lane',
            'number': '121',
            'city': 'Anchorage',
            'postalCode': '12345',
            'country': 'US'
        })
    
    def mock_address2(self):
        return Address.from_dict({
            'street': 'Cannon HOB',
            'number': '153',
            'city': 'Washington',
            'postalCode': '20515',
            'country': 'US'
        })

    def mock_request(self):
        return ScanRequestDTO.from_dict({
            'scanId': '123',
            'clientId': '456',
            'userId': '789',
            'addresses': [self.mock_address1().to_dict(), self.mock_address2().to_dict()],
            'names': ['Mary Sattler Peltola', 'Mary Peltola'],
            'emails': ['team@marypeltola.com'],
            'webDomains': [],
            'phones': ['1(907) 921-6575', '225-5765'], # make the first one longer than the one on the site, and the second one shorter than the one on the site, so we can test the phone number matching in both cases
            'companies': ['U.S. REPRESENTATIVE', 'Team Peltola'],
            'images': ['https://peltola.house.gov/uploadedphotos/highresolution/56440a66-676c-41c0-8767-8b7bc549ac6d.jpg']
        })

    def test_search(self):
        # mock scan dto
        scan_dto = ScanDTO(self.mock_request())
        scan_dto.user_image_faces = [UserImageFace('s3someid', [0.111222333]*512)]

        web_searcher = WebSearcher()
        search_results = web_searcher.search(scan_dto)
        
        print(f'# of search_results: {len(search_results)}')

        # test no duplicates of url in search results - duplicate is allowed in searcher and prevented in dme-detector
        # urls = [sr.url for sr in search_results]
        # self.assertEqual(len(urls), len(set(urls)))

        # test one of the results (wikipedia) that contain multiple image search results and the right title & site url
        wikipedia_results = [sr for sr in search_results if sr.url == 'https://en.wikipedia.org/wiki/Mary_Peltola']
        self.assertTrue(len(wikipedia_results) > 1)
        self.assertTrue(len(wikipedia_results[0].image_search_urls) > 0)
        self.assertEqual(wikipedia_results[0].title, 'Mary Peltola - Wikipedia')
        self.assertEqual(wikipedia_results[0].domain, 'en.wikipedia.org')

        # took ~ 25 seconds to run this test

