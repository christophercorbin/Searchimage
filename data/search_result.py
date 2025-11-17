from typing import List
from data.leak_dto import LeakDTO
from data.face_match_dto import FaceMatchDto

class SearchResult():
    def __init__(self, url, title, domain, image_urls, search_term='', page=-1, position=-1):
        self.url = url
        self.title = title
        self.domain = domain
        self.search_term = search_term if search_term else '' # when '', it means the search result came from vector DB search, not from a website search
        self.page = page # page number of where this result was found
        self.position = position # position on page

        # if image_urls is a str, not an array, convert it to an array
        if isinstance(image_urls, str):
            image_urls = [image_urls]
        # this is the image url resulted from image search, empty if it was a regular site search (there could be multiple if image search returned multiple results from the same site with same link)
        # use the array of image urls if not empty, otherwise create an empty array
        self.image_search_urls = image_urls if image_urls is not None and len(image_urls) > 0 else []

        # this is the list of face vectors that matched the provided user face on this website - no need to analyze them again when adding to leaks db
        self.matched_faces: List[FaceMatchDto] = []

        self.visited = False
        self.leak: LeakDTO = None # content scraped from the site, including user personal information and all images extracted on the site
    
    def add_image_url(self, image_url, search_term='', page=-1, position=-1):
        # if the image url is not already in the list, add it
        if image_url not in self.image_search_urls:
            self.image_search_urls.append(image_url)

        # add the search term, page and position if they are not already set
        if self.search_term == '' and search_term != '':
            self.search_term = search_term

        if self.page == -1 and page != -1:
            self.page = page

        if self.position == -1 and position != -1:
            self.position = position

    def to_dict(self):
        return {
            'url': self.url,
            'title': self.title,
            'domain': self.domain,
            'searchTerm': self.search_term,
            'page': self.page,
            'position': self.position,
            'imageSearchUrls': self.image_search_urls,
            'matchedFaces': [mf.to_dict() for mf in self.matched_faces],
            'visited': self.visited,
            'leak': self.leak.to_dict() if self.leak is not None else None
        }
    
    @staticmethod
    def from_dict(d:dict):
        return SearchResult(
            d.get('url'), 
            d.get('title'), 
            d.get('domain'), 
            d.get('imageSearchUrls'), 
            d.get('searchTerm'), 
            d.get('page'), 
            d.get('position'))