class FaceVectorDto():
    def __init__(self, img_src_url, img_storage_id, face_storage_id, site_title, site_url, score, doc_id):
        self.img_src_url = img_src_url
        self.img_storage_id = img_storage_id
        self.face_storage_id = face_storage_id
        self.site_title = site_title
        self.site_url = site_url
        self.score = score
        self.doc_id = doc_id

    def to_dict(self):
        return {
            "imgSrcUrl": self.img_src_url,
            "imgStorageId": self.img_storage_id,
            "faceStorageId": self.face_storage_id,
            "siteTitle": self.site_title,
            "siteUrl": self.site_url,
            "score": self.score,
            "docId": self.doc_id
        }
    
    @staticmethod
    def from_dict(data):
        return FaceVectorDto(
            img_src_url=data.get('imgSrcUrl'),
            img_storage_id=data.get('imgStorageId'),
            face_storage_id=data.get('faceStorageId'),
            site_title=data.get('siteTitle'),
            site_url=data.get('siteUrl'),
            score=data.get('score'),
            doc_id=data.get('docId')
        )