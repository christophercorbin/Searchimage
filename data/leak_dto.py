from typing import List
from data.address import Address
from data.site_image_dto import SiteImageDTO

class LeakDTO():
    def __init__(self, addresses: List[Address] = [], names: List[str] = [], emails: List[str] = [], web_domains: List[str] = [], phones: List[str] = [], companies: List[str] = [], site_image_urls: List[str] = []):
        self.addresses = addresses
        self.names = names
        self.emails = emails
        self.web_domains = web_domains
        self.phones = phones
        self.companies = companies
        self.site_image_urls = site_image_urls

    def to_dict(self):
        return {
            "addresses": [address.to_dict() for address in self.addresses] if self.addresses is not None else [],
            "names": self.names,
            "emails": self.emails,
            "webDomains": self.web_domains,
            "phones": self.phones,
            "companies": self.companies,
            "siteImageUrls": self.site_image_urls
        }
    
    @staticmethod
    def from_dict(data):
        return LeakDTO(
            addresses=[Address.from_dict(address) for address in data.get('addresses')] if data.get('addresses') is not None else [],
            names=data.get('names'),
            emails=data.get('emails'),
            web_domains=data.get('webDomains'),
            phones=data.get('phones'),
            companies=data.get('companies'),
            site_image_urls=data.get('siteImageUrls')
        )
