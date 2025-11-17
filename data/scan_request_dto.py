import json
from data.address import Address
from typing import List

class ScanRequestDTO():
    def __init__(self, scan_id, client_id='', user_id='', addresses:List[Address]=[], names=[], emails=[], web_domains=[], phones=[], companies=[], images=[], companyDomains=[]):
        self.scan_id = scan_id
        self.client_id = client_id
        self.user_id = user_id
        self.addresses = addresses if addresses is not None else []
        self.names = names if names is not None else []
        self.emails = emails if emails is not None else []
        self.web_domains = web_domains if web_domains is not None else []
        self.phones = phones if phones is not None else []
        self.companies = companies if companies is not None else []
        self.companyDomains = companyDomains if companyDomains is not None else []
        self.user_imgs = images if images is not None else []

    def to_dict(self):
        return {
            "scanId": self.scan_id,
            "clientId": self.client_id,
            "userId": self.user_id,
            "addresses": [address.to_dict() for address in self.addresses] if self.addresses is not None else [],
            "names": self.names,
            "emails": self.emails,
            "webDomains": self.web_domains,
            "phones": self.phones,
            "companies": self.companies,
            "companyDomains": self.companyDomains,
            "images": self.user_imgs
        }
    
    @staticmethod
    def from_dict(data):
        return ScanRequestDTO(
            scan_id=data.get('scanId'),
            client_id=data.get('clientId'),
            user_id=data.get('userId'),
            addresses=[Address.from_dict(address) for address in data.get('addresses')] if data.get('addresses') is not None else [],
            names=data.get('names'),
            emails=data.get('emails'),
            web_domains=data.get('webDomains'),
            phones=data.get('phones'),
            companies=data.get('companies'),
            companyDomains=data.get('companyDomains'),
            images=data.get('images')
        )
