from typing import List
from datetime import datetime, timezone
from data.address import Address
from bson.objectid import ObjectId

class Leak():
    def __init__(self, addresses: List[Address] = [], names: List[str] = [], emails: List[str] = [], web_domains: List[str] = [], phones: List[str] = [], companies: List[str] = [], img_doc_ids: List[ObjectId] = []) -> None:
        self.addresses = addresses
        self.names = names
        self.emails = emails
        self.web_domains = web_domains
        self.phones = phones
        self.companies = companies
        self.img_doc_ids = img_doc_ids

    def to_dict(self):
        return {
            "addresses": [address.to_dict() for address in self.addresses],
            "names": self.names,
            "emails": self.emails,
            "webDomains": self.web_domains,
            "phones": self.phones,
            "companies": self.companies,
            "imgDocIds": self.img_doc_ids
        }
    
    @staticmethod
    def from_dict(data):
        return Leak(
            addresses=[Address.from_dict(address) for address in data.get('addresses')],
            names=data.get('names'),
            emails=data.get('emails'),
            web_domains=data.get('webDomains'),
            phones=data.get('phones'),
            companies=data.get('companies'),
            img_doc_ids=data.get('imgDocIds')
        )

class LeakEntity():
    def __init__(self, site_title, site_url, found_on = None, scan_id: str = '', client_id: str = '', user_id: str = '', leak: Leak = None, _id:ObjectId = None) -> None:
        self._id = _id if _id else ObjectId()
        self.scan_id = scan_id
        self.client_id = client_id
        self.user_id = user_id
        self.title = site_title
        self.url = site_url
        self.found_on = found_on if found_on is not None else datetime.now(timezone.utc).isoformat()
        self.leaks = leak # leaks found on the site

    def to_dict(self):
        return {
            "scanId": self.scan_id,
            "clientId": self.client_id,
            "userId": self.user_id,
            "title": self.title,
            "url": self.url,
            "foundOn": self.found_on,
            "leaks": self.leaks.to_dict()
        }
    
    @staticmethod
    def from_dict(data):
        return LeakEntity(
            _id=data.get('_id'),
            scan_id=data.get('scanId'),
            client_id=data.get('clientId'),
            user_id=data.get('userId'),
            site_title=data.get('title'),
            site_url=data.get('url'),
            found_on=data.get('foundOn'),
            leak=Leak.from_dict(data.get('leaks'))
        )
    

    

