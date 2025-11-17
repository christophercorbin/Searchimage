from data.address import Address
from typing import List
from datetime import datetime, timezone

class WebsiteEntity():
    def __init__(self, site_url, title, names=[], emails=[], phones=[], addresses:List[Address]=[], companies=[], created_at=None, updated_at=None):
        self.site_url = site_url
        self.title = title
        self.names = names
        self.emails = emails
        self.phones = phones
        self.addresses = addresses
        self.companies = companies
        self.created_at = created_at if created_at is not None else datetime.now(timezone.utc).isoformat()
        self.updated_at = updated_at if updated_at is not None else datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "siteUrl": self.site_url,
            "title": self.title,
            "names": self.names,
            "emails": self.emails,
            "phones": self.phones,
            "addresses": [address.to_dict() for address in self.addresses],
            "companies": self.companies,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        return WebsiteEntity(
            site_url=data.get('siteUrl'),
            title=data.get('title'),
            names=data.get('names'),
            emails=data.get('emails'),
            phones=data.get('phones'),
            addresses=[Address.from_dict(address) for address in data.get('addresses')],
            companies=data.get('companies'),
            created_at=data.get('createdAt'),
            updated_at=data.get('updatedAt')
        )