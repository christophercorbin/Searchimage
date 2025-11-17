class SiteImageDTO():
    def __init__(self, base_url, imgurl):
        self.base_url = base_url
        self.imgurl = imgurl

    def to_dict(self):
        return {
            "base_url": self.base_url,
            "imgurl": self.imgurl
        }
    
    @staticmethod
    def from_dict(data):
        return SiteImageDTO(
            base_url=data.get('base_url'),
            imgurl=data.get('imgurl')
        )