import json
from datetime import datetime, timezone
from bson.objectid import ObjectId

class ScanEntity():
    def __init__(self, scan_id, client_id='', user_id='', payload=None, leak_ids=[], status='', trace='', found=0, processed=0, created_at=None, updated_at=None, _id: ObjectId = None):
        self._id = _id if _id else ObjectId()
        self.scan_id = scan_id
        self.client_id = client_id
        self.user_id = user_id
        self.payload =payload
        self.leak_ids = leak_ids
        self.status = status
        self.trace = trace
        self.found = found
        self.processed = processed
        self.created_at = created_at if created_at is not None else datetime.now(timezone.utc).isoformat()
        self.updated_at = updated_at if updated_at is not None else datetime.now(timezone.utc).isoformat()


    def to_dict(self):
        return {
            "scanId": self.scan_id,
            "clientId": self.client_id,
            "userId": self.user_id,
            "payload": self.payload,
            "leakIds": self.leak_ids,
            "status": self.status,
            "trace": self.trace,
            "found": self.found,
            "processed": self.processed,     
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
    
    @staticmethod
    def from_dict(data:dict):
        return ScanEntity(
            _id=data.get('_id'),
            scan_id=data.get('scanId'),
            client_id=data.get('clientId'),
            user_id=data.get('userId'),
            payload=data.get('payload'),
            leak_ids=data.get('leakIds'),
            status=data.get('status'),
            trace=data.get('trace'),
            found=data.get('found'),
            processed=data.get('processed'),
            created_at=data.get('createdAt'),
            updated_at=data.get('completedAt')
        )
    
    

