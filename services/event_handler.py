import logging
import json
from clients.db import DbClient
from config import Config
from clients.event_producer import EventProducer
from data.scan_request_dto import ScanRequestDTO
from data.scan_dto import ScanDTO
from data.search_result import SearchResult
from services.user_service import UserService
from services.scan_service import ScanService
from services.web_searcher import WebSearcher
from services.vector_searcher import VectorSearcher
from data.scan_status_enum import ScanStatusEnum
from data.detector_request_dto import DetectorRequestDTO
from repositories.storage_s3_repo import StorageS3Repo
from repositories.opensearch_repo import OpenSearchRepo
import os
import shutil
import json
from typing import List

class EventHandler():
    def __init__(self, flow:str='quick'):
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_EVENT_HANDLER_DME_SEARCHER)
        self._db_client = DbClient().get_client()
        self._storage = StorageS3Repo()
        self._vector_db = OpenSearchRepo()
        self._scan_service = ScanService(self._db_client)
        self._user_service = UserService(self._db_client, self._storage)
        self._web_searcher = WebSearcher(flow)
        self._vector_searcher = VectorSearcher(self._vector_db)
        self._producer = EventProducer()
        self._flow = flow

    def process(self, event):
        scan_dto: ScanDTO = None
        request = ScanRequestDTO.from_dict(json.loads(event))
        self._logger.info(f'DME searcher received: {request.to_dict()}')
        scan_entity = None
        scan_dto = ScanDTO(request)
        try:
            scan_entity = self._scan_service.update_scan_state(request, ScanStatusEnum.IN_PROGRESS)
        except Exception as e:
            # something went wrong with the scan event, skip processing it
            self._logger.error(f'Error updating scan status: {e}')
            return

        # prepare the uploaded user images for similarity calculation with images found on the web later
        if len(request.user_imgs) > 0:
            self._user_service.process_user_images(request.user_imgs, scan_dto)

        # search on the web for new exposures (images, websites, etc.), use backup serper in case of failure
        search_results = self._web_searcher.search(scan_dto)
            
        #search in face vectors with the user image faces provided
        if scan_dto.user_image_faces: # temp fix to avoid false positives
            search_results = self._vector_searcher.search(search_results, scan_dto.user_image_faces)

        if request.user_id:
            # if this is an existing user with leaks - filter out the search results that are already in her leak records
            search_results = self._user_service.filter_search_results(request.client_id, request.user_id, search_results)

        # process the search results and update the scan record
        self._scan_service.update_scan_found_count(scan_entity, len(search_results))

        # initialize a search stats record for this scan
        self._scan_service.add_search_stat(search_results, request.scan_id)

        # dispacth the search results for workers to process
        for sr in search_results:
            request = DetectorRequestDTO(scan_id=scan_dto.scan_id, search_result=sr, client_id=scan_dto.client_id, user_id=scan_dto.user_id, 
                                         addresses=request.addresses, names=request.names, emails=request.emails, web_domains=request.web_domains, 
                                         phones=request.phones, companies=request.companies, companyDomains=request.companyDomains, images=request.user_imgs)
            
            # search results with the same search term will be dispatched to the same worker so orders of search relevance are preserved for each search term
            if self._flow != 'quick':
                self._producer.produce(self._configs.EVENT_TOPIC_DME_DETECTOR_FULL, json.dumps(request.to_dict()), sr.search_term)
            else:
                self._producer.produce(self._configs.EVENT_TOPIC_DME_DETECTOR_QUICK, json.dumps(request.to_dict()), sr.search_term)
                
        if len(search_results)==0: # we do not find any urls to process by detector workers
            try:
                scan_entity = self._scan_service.update_scan_state(request, ScanStatusEnum.COMPLETED)
            except Exception as e:
                # something went wrong with the scan event, skip processing it
                self._logger.error(f'Error updating scan status: {e}')
                return                

        # clean up
        # Purge the temp folder for this user.
        if self._configs.PURGE_SCRAPPED_DATA is True and os.path.exists(scan_dto.user_images_local_dir):
            shutil.rmtree(scan_dto.user_images_local_dir)

        self._logger.info(f'### DME searcher completed for id: {request.scan_id}')

    def close(self):
        self._db_client.close()


        
        

        

        

        
            
            

