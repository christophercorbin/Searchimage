from services.web_searcher import WebSearcher
import unittest
from data.address import Address
from data.scan_request_dto import ScanRequestDTO
from data.scan_dto import ScanDTO, UserImageFace

class TestWebSearcher(unittest.TestCase):
    def mock_address0(self):
        return Address.from_dict({
            'street': 'Chame-Chame',
            'number': '133',
            'city': 'Salvador',
            'postalCode': '40140-902',
            'country': 'Brazil'
        })

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
            'addresses': [self.mock_address0().to_dict(), self.mock_address1().to_dict(), self.mock_address2().to_dict()],
            'names': ['Mary Sattler Peltola', 'Mary Peltola'],
            'emails': ['team@marypeltola.com', 'peltola@gmail.com', 'mary@hotmail.com'],
            'webDomains': [],
            'phones': ['1(907) 921-6575', '225-5765'], # make the first one longer than the one on the site, and the second one shorter than the one on the site, so we can test the phone number matching in both cases
            'companies': ['U.S. REPRESENTATIVE', 'Team Peltola', 'DemoCo - Get your score.', 'MaryPeltola'],
            'images': ['https://peltola.house.gov/uploadedphotos/highresolution/56440a66-676c-41c0-8767-8b7bc549ac6d.jpg']
        })
    
    def mock_request_empty_strings_in_user_pii(self):
        return ScanRequestDTO.from_dict({
            'scanId': '123',
            'clientId': '456',
            'userId': '789',
            'addresses': [],
            'names': [''],
            'emails': [''],
            'webDomains': [''],
            'phones': [''],
            'companies': [''],
            'images': ['']
        })
    
    def mock_request_empty_company(self):
        return ScanRequestDTO.from_dict({
            'scanId': '123',
            'clientId': '456',
            'userId': '789',
            'addresses': [self.mock_address1().to_dict(), self.mock_address2().to_dict()],
            'names': ['Mary Sattler Peltola', 'Mary Peltola'],
            'emails': ['peltola@gmail.com', 'mary@hotmail.com'],
            'webDomains': [],
            'phones': ['1(907) 921-6575', '225-5765'], # make the first one longer than the one on the site, and the second one shorter than the one on the site, so we can test the phone number matching in both cases
            'companies': [],
            'images': ['https://peltola.house.gov/uploadedphotos/highresolution/56440a66-676c-41c0-8767-8b7bc549ac6d.jpg']
        })

    def test_formulate_image_search_terms(self):
        # mock scan dto
        scan_dto = ScanDTO(self.mock_request())
        scan_dto.user_image_faces = [UserImageFace('s3someid', [0.111222333]*512)]
        
        web_searcher = WebSearcher()
        terms = web_searcher.formulate_image_search_terms(scan_dto)
        print(f'search terms: {terms}')
        self.assertEqual(len(terms), 5)
        self.assertTrue('Mary Sattler Peltola' in terms)
        self.assertTrue('Mary Peltola' in terms)
        self.assertTrue('U.S. REPRESENTATIVE Mary Sattler Peltola' in terms)
        self.assertTrue('Team Peltola Mary Sattler Peltola' in terms)
        self.assertTrue('MaryPeltola Mary Sattler Peltola' in terms) # company name from email
        self.assertFalse('DemoCo - Get your score. Mary Sattler Peltola' in terms) # filter out fake company name
        self.assertFalse('gmail Mary Sattler Peltola' in terms) # filter out common email provider as company name
        self.assertFalse('hotmail Mary Peltola' in terms) # filter out common email provider as company name

    def test_formulate_site_search_terms(self):
        # mock scan dto
        scan_dto = ScanDTO(self.mock_request())
        scan_dto.user_image_faces = [UserImageFace('s3someid', [0.111222333]*512)]
        
        web_searcher = WebSearcher()
        terms = web_searcher.formulate_site_search_terms(scan_dto)
        print(f'search terms: {terms}')
        self.assertEqual(len(terms), 13)
        self.assertTrue('team@marypeltola.com' in terms)
        self.assertTrue('peltola@gmail.com' in terms)
        self.assertTrue('mary@hotmail.com' in terms)
        self.assertTrue('1(907) 921-6575' in terms)
        self.assertTrue('225-5765' in terms)
        self.assertTrue('Mary Sattler Peltola' in terms)
        self.assertTrue('Mary Peltola' in terms)
        self.assertTrue('U.S. REPRESENTATIVE Mary Sattler Peltola' in terms)
        self.assertTrue('Team Peltola Mary Sattler Peltola' in terms)
        self.assertTrue('MaryPeltola Mary Sattler Peltola' in terms)
        self.assertTrue('121 West Fireweed Lane Anchorage 12345' in terms)
        self.assertTrue('153 Cannon HOB Washington 20515' in terms)
        self.assertFalse('DemoCo - Get your score. Mary Sattler Peltola' in terms) # filter out fake company name
        self.assertFalse('gmail Mary Sattler Peltola' in terms)
        self.assertFalse('hotmail Mary Peltola' in terms)

    def test_formulate_image_search_terms_with_empty_company(self):
        # mock scan dto
        scan_dto = ScanDTO(self.mock_request_empty_company())
        scan_dto.user_image_faces = [UserImageFace('s3someid', [0.111222333]*512)]
        
        web_searcher = WebSearcher()
        terms = web_searcher.formulate_image_search_terms(scan_dto)
        print(f'search terms: {terms}')
        self.assertEqual(len(terms), 2)
        self.assertTrue('Mary Sattler Peltola' in terms)
        self.assertTrue('Mary Peltola' in terms)

    def test_formulate_site_search_terms_with_empty_company(self):
        # mock scan dto
        scan_dto = ScanDTO(self.mock_request_empty_company())
        scan_dto.user_image_faces = [UserImageFace('s3someid', [0.111222333]*512)]
        
        web_searcher = WebSearcher()
        terms = web_searcher.formulate_site_search_terms(scan_dto)
        print(f'search terms: {terms}')
        self.assertEqual(len(terms), 8)

    def test_get_companies(self):
        request = ScanRequestDTO('mock-scan-id')
        request.companies = ['Apple', 'apple', 'Google', 'TestFilteredCompany co', 'DemoCo - Get your score.']
        request.emails = ['person@custom-domain.com', 'other@Custom-Domain.com']
        expected_companies = ['Apple', 'Google', 'custom-domain']
        web_searcher = WebSearcher()
        result = web_searcher.get_companies(request)
        self.assertEqual(sorted(result), sorted(expected_companies))

    def test_scan_dto_location_info(self):
        # mock scan dto
        scan_dto = ScanDTO(self.mock_request())

        location_code = scan_dto.location_code
        in_country = scan_dto.in_country
        self.assertTrue(2076 == location_code) # lcoation code from the country 
        self.assertTrue('br' in in_country)    # country_iso_code from the country 

    def test_formulate_site_search_terms_with_empty_strings_result_in_no_search_terms(self):
        # mock scan dto
        scan_dto = ScanDTO(self.mock_request_empty_strings_in_user_pii())        
        web_searcher = WebSearcher()
        terms = web_searcher.formulate_site_search_terms(scan_dto)
        print(f'search terms: {terms}')
        self.assertEqual(len(terms), 0)

    def test_formulate_image_search_terms_with_empty_strings_result_in_no_search_terms(self):
        # mock scan dto
        scan_dto = ScanDTO(self.mock_request_empty_strings_in_user_pii())        
        web_searcher = WebSearcher()
        terms = web_searcher.formulate_image_search_terms(scan_dto)
        print(f'search terms: {terms}')
        self.assertEqual(len(terms), 0)

