from data.scan_dto import ScanDTO
from config import Config
import requests
import json
import logging
from data.scan_request_dto import ScanRequestDTO
from data.search_result import SearchResult
from typing import List
from services.util_service import UtilService
import time

class WebSearcher():
    def __init__(self, flow:str='quick'):
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_WEB_SEARCHER)
        self._max_search_page = self._configs.MAX_PAGES_TO_SEARCH_QUICK if flow == 'quick' else self._configs.MAX_PAGES_TO_SEARCH_FULL
        self._max_search_result_per_page = self._configs.MAX_SEARCH_RESULTS_PER_PAGE_QUICK if flow == 'quick' else self._configs.MAX_SEARCH_RESULTS_PER_PAGE_FULL
        self._images_searcher_url = 'https://google.serper.dev/images'
        self._sites_searcher_url = 'https://google.serper.dev/search'
        self._searcher_headers = {
            'X-API-KEY': self._configs.IMAGE_DOWNLOADER_API_KEY,
            'Content-Type': 'application/json'
        }


    def search(self, scan_dto: ScanDTO) -> List[SearchResult]:
        """
        - formulate search terms for web images search
        - formulate search terms for web sites search
        - search for images using image search terms
        - search for sites using site search terms
        - consolidate the two search results, remove duplicates

        :returns: a list of websites to inspect for user info leaks
        """
        search_results: List[SearchResult] = []
        
        # skip image search if no user images provided
        # image search will be based on all the names provided + the first name provided & the first company name provided (current design)
        # TODO: add more search terms for image search based on all names & company names combination
        if len(scan_dto.user_image_faces) > 0:
            search_terms = self.formulate_image_search_terms(scan_dto)
            self.search_images(search_terms, scan_dto.in_country, search_results)

        # site search will base on user's personal information provided
        search_terms = self.formulate_site_search_terms(scan_dto)
        self.search_sites(search_terms, scan_dto.in_country, search_results)

        self._logger.info(f'Found {len(search_results)} search results')

        return search_results


    def formulate_image_search_terms(self, scan_dto: ScanDTO) -> List[str]:
        terms = [name for name in scan_dto.request.names if name]

        if len(scan_dto.request.companies) > 0 and len(terms) > 0:
            # search companies with the first user name provided, TODO: support all user names / aliases?
            companies = self.get_companies(scan_dto.request)
            for company in companies:
                if company:
                    terms.append(f'{company} {scan_dto.request.names[0]}')

        return terms


    def formulate_site_search_terms(self, scan_dto: ScanDTO) -> List[str]:
        terms = [email for email in scan_dto.request.emails if email]
        terms += [phone for phone in scan_dto.request.phones if phone]
        terms += [name for name in scan_dto.request.names if name]

        if len(scan_dto.request.companies) > 0 and len(scan_dto.request.names) > 0:
            # search companies with the first user name provided, TODO: support all user names / aliases?
            companies = self.get_companies(scan_dto.request)
            for company in companies:
                if company:
                    terms.append(f'{company} {scan_dto.request.names[0]}')
        if len(scan_dto.request.addresses) > 0:
            # search all addresses
            for address in scan_dto.request.addresses:
                terms.append(f'{address.number} {address.street} {address.city} {address.postal_code}')
        
        return terms


    def search_images(self, search_terms, in_country, search_results:List[SearchResult]) -> List[SearchResult]:
        for term in search_terms:
            search_results = self.search_images_by_term(term, in_country, search_results)

        return search_results
    

    def search_images_by_term(self, term, in_country, search_results:List[SearchResult]) -> List[SearchResult]:
        for page in range(1, self._max_search_page + 1):
            payload = json.dumps({
                "q": term,
                "gl": in_country,
                "autocorrect": True,
                "page": page,
                "num": self._max_search_result_per_page
            })

            response = requests.request(
                "POST", 
                self._images_searcher_url,
                headers=self._searcher_headers, 
                data=payload)
            
            image_dicts = []
            if response.status_code == 200:
                body = json.loads(response.text)
                image_dicts = body.get('images', [])
                self.parse_image_search_results(image_dicts, search_results, term, page)
            else:
                self._logger.info(f'Error searching for images for term {term} and page {page}. Response status code: {response.status_code}')
                break

            # stop condition: if the number of results is less than the max results per page
            if (len(image_dicts) < self._max_search_result_per_page):
                break

        return search_results


    def parse_image_search_results(self, image_dicts:List[dict], search_results:List[SearchResult], search_term:str, page:int) -> List[SearchResult]:        
        for image_dict in image_dicts:
            search_results.append(SearchResult(
                image_dict.get('link'), 
                image_dict.get('title'), 
                image_dict.get('domain'), 
                [image_dict.get('imageUrl')], 
                search_term=f'{search_term}-images',
                page=page,
                position=image_dict.get('position')))

        return search_results


    def search_sites(self, search_terms: List[str], in_country, search_results:List[SearchResult]) -> List[SearchResult]:
        for term in search_terms:
            search_results = self.search_sites_by_term(term, in_country, search_results)

        return search_results
        

    def search_sites_by_term(self, term, in_country, search_results:List[SearchResult]) -> List[SearchResult]:
        for page in range(1, self._max_search_page + 1):
            search_request = json.dumps({
                        'q': term,
                        'gl': in_country,
                        'autocorrect': True,
                        'page': page,
                        'num': self._max_search_result_per_page
                    })

            response = requests.request(
                "POST", 
                self._sites_searcher_url, 
                headers=self._searcher_headers, 
                data=search_request)

            site_dicts = []
            if response.status_code == 200:
                body = json.loads(response.text)
                site_dicts = body.get('organic', [])
                self.parse_site_search_results(site_dicts, search_results, term, page)
            else:
                self._logger.info(f'Error searching for sites for term {term}. Response status code: {response.status_code}')
                break

            # stop condition: if the number of results is less than the max results per page
            if (len(site_dicts) < self._max_search_result_per_page):
                break

        return search_results


    def parse_site_search_results(self, site_dicts:List[dict], search_results:List[SearchResult], search_term:str, page:int) -> List[SearchResult]:
        for site_dict in site_dicts:
            search_results.append(SearchResult(site_dict.get('link'), 
                                                site_dict.get('title'), 
                                                site_dict.get('domain'), 
                                                None, 
                                                search_term=search_term,
                                                page=page,
                                                position=site_dict.get('position')))

        return search_results
    
    def get_companies(self, request: ScanRequestDTO) -> List[str]:
        '''
        Company names will come from 1) the request object and 2) user's work email domain
        '''
        companies = []

        if len(request.companies) > 0:
            filtered_companies = [company for company in request.companies if company not in self._configs.COMPANY_NAME_FILTER]
            if (filtered_companies):
                companies.extend(filtered_companies)

        if len(request.emails) > 0:
            root_domains = UtilService.get_work_email_root_domains(request.emails)
            if (root_domains):
                companies.extend(root_domains)

        # Remove duplicates, ignoring case, while preserving the original case
        unique_companies = {}
        for company in companies:
            # Use the lower case version of the company name as the key for case-insensitive comparison
            key = company.lower()
            if key not in unique_companies:
                unique_companies[key] = company

        # Return a list of unique companies preserving the original case
        return list(unique_companies.values())
        
