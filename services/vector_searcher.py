from repositories.vector_db_repo_abc import VectorDbRepoABC
from data.search_result import SearchResult
from data.scan_dto import ScanDTO
from data.face_vector_dto import FaceVectorDto
from data.face_match_dto import FaceMatchDto
from data.scan_dto import UserImageFace
from typing import List
from config import Config
import logging

class VectorSearcher():
    def __init__(self, vector_db: VectorDbRepoABC) -> None:
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_VECTOR_SEARCHER)
        self._vector_db = vector_db

    def search(self, search_results: List[SearchResult], user_faces: List[UserImageFace]) -> List[SearchResult]:
        """
        Searches for matches in the vector database.
        For each macthed vector, if it has a site url that already exists in the search results, add matched vector to that search result.
        If there is no search result for the matched vector, create a new search result and add it to the list.

        Args:
            search_results (List[SearchResult]): list of search results to be updated
            user_faces (List[UserImageFace]): list of user faces to be searched
        """
        try:
            matched_faces = self._search_vectors(user_faces)
            for mf in matched_faces:
                match_face_added = False

                # if the vector contains a site url that already exists in the search results, add the matched vector to that search result if it doesn't already exist
                for search_result in search_results:
                    if search_result.url == mf.matched_face_vector.site_url:
                        # now check if the matched vector is already in the search result before adding it
                        if mf.matched_face_vector.img_src_url not in [mf.matched_face_vector.img_src_url for mf in search_result.matched_faces]:
                            search_result.matched_faces.append(mf)
                            # break - do not break here as there might be multiple search results with the same url
                        
                        # the matched face is / was already added to a search result with the same site url
                        match_face_added = True

                if not match_face_added:
                    # if there is no search result for the matched vector, create a new search result and add it to the list
                    search_result = SearchResult(mf.matched_face_vector.site_url, mf.matched_face_vector.site_title, mf.matched_face_vector.site_url, [])
                    search_result.matched_faces.append(mf)
                    search_results.append(search_result)

            return search_results
    
        except Exception as e:
            self._logger.error(f'Error searching vectors: {e}')
            return []


    def _search_vectors(self, user_faces: List[UserImageFace]) -> List[FaceMatchDto]:
        """
        Searches for vectors in the vector database.

        Args:
            vectors (List[str]): list of vectors to be searched

        Returns:
            List[SearchResult]: list of search results
        """

        results: List[FaceMatchDto] = []
        for uf in user_faces:
            vectors = self._vector_db.search(uf.face_vector, num=self._configs.MAX_NUM_FACE_VECTORS_TO_SEARCH, 
                                 min_score=self._configs.MIN_SIMILARITY_SCORE_VECTOR_DB)
            
            for v in vectors:
                results.append(FaceMatchDto(uf.store_id, v))
        return results
            
        