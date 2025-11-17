'''
PYTHONPATH=$PYTHONPATH:/home/ubuntu/data-mining-engine:/home/ubuntu/data-mining-engine/data
export PYTHONPATH
'''

from pymongo import MongoClient
from pymongo.collection import ReturnDocument
from data.scan_entity import ScanEntity
from config import Config
import logging

class ScanRepo():
    def __init__(self, db_client: MongoClient, db_name, collection_name):
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_SCAN_REPO)
        self._client = db_client
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]

    def add(self, scan_entity: ScanEntity):
        # Convert the ScanEntity to a dict before insertion
        result = self._collection.insert_one(scan_entity.to_dict())
        return result.inserted_id
    
    def get_by_scan_id(self, scan_id) -> ScanEntity:
        # Get the scan by its id
        scan_doc = self._collection.find_one({'scanId': scan_id})
        if scan_doc is None:
            return None
        else:
            return ScanEntity.from_dict(scan_doc)
                                        
    def update_scan(self, scan_entity: ScanEntity) -> ScanEntity:
        # Update the scan by ObjectId
        scan_doc = self._collection.find_one_and_update(
            {'_id': scan_entity._id},
            {'$set': scan_entity.to_dict()},
            return_document=ReturnDocument.AFTER
        )

        return ScanEntity.from_dict(scan_doc)


if __name__ == '__main__':
    configs = Config.get()
    print('### testing scan repo')
    scan_repo = ScanRepo(configs.DB_URL, configs.DB_NAME, configs.SCAN_REPO_NAME)
    scan_entity = ScanEntity(
        scan_id='scan_id',
        client_id='client_id',
        user_id='user_id',
        payload='some-more-more-more-payload',
        leak_ids=['website_urls'],
        status='status',
        trace='trace'
    )
    # scan_id = scan_repo.add(scan_entity)
    scan = scan_repo.update_scan(scan_entity)
    print(scan)