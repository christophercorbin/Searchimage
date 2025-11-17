from data.scan_request_dto import ScanRequestDTO
from data.scan_entity import ScanEntity
from data.scan_status_enum import ScanStatusEnum
from data.search_stat_entity import SearchStatEntity
from typing import List
from data.search_result import SearchResult
from repositories.scan_repo import ScanRepo
from repositories.search_stat_repo import SearchStatRepo
from config import Config
from pymongo import MongoClient
import logging
from datetime import datetime, timezone

class ScanService():
    def __init__(self, db_client: MongoClient):
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_SCAN_SERVICE)
        self._scan_repo = ScanRepo(db_client, self._configs.DB_NAME, self._configs.SCAN_REPO_NAME)
        self._search_stats_repo = SearchStatRepo(db_client, self._configs.DB_NAME, self._configs.SEARCH_STATS_REPO_NAME)

    def update_scan_state(self, scan_request: ScanRequestDTO, status: ScanStatusEnum) -> ScanEntity:
        '''
        Update the scan state in db
        '''
        scan: ScanEntity = self._scan_repo.get_by_scan_id(scan_request.scan_id)
        if not scan:
            self._logger.error(f'### scan not found: {scan_request.scan_id}')
            raise Exception(f'### scan not found: {scan_request.scan_id}')
        
        scan.status = status.value
        scan.updated_at = datetime.now(timezone.utc).isoformat()
        return self._scan_repo.update_scan(scan)


    def update_scan_found_count(self, scan: ScanEntity, found_count: int) -> ScanEntity:
        scan.found = found_count
        scan.updated_at = datetime.now(timezone.utc).isoformat()  
        return self._scan_repo.update_scan(scan)


    def add_search_stat(self, search_results: List[SearchResult], scan_id: str):
        search_stat_entity = SearchStatEntity(scan_id, search_results)
        return self._search_stats_repo.add(search_stat_entity)

    