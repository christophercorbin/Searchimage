import unittest
from data.search_stat_entity import SearchStatEntity
from data.search_result import SearchResult

class TestSearchStatEntity(unittest.TestCase):
    def test_create_search_stat_entity_happy_path(self):
        # Arrange
        scan_id = "scan_id"
        search_results = [
            SearchResult(url='url1', title='title1', domain='domain1', image_urls=[], search_term='term #1', page=1, position=1),
            SearchResult(url='url2', title='title2', domain='domain2', image_urls=[], search_term='term #1', page=1, position=2),
            SearchResult(url='url3', title='title3', domain='domain3', image_urls=[], search_term='term #2', page=1, position=1),
            SearchResult(url='url4', title='title4', domain='domain4', image_urls=[], search_term='term #2', page=1, position=2)
        ]

        # Act
        search_stat_entity = SearchStatEntity(scan_id, search_results)

        # Assert
        self.assertEqual(search_stat_entity.scan_id, scan_id)
        self.assertEqual(search_stat_entity.stats, [
            {'term': 'term #1', 'total': 2, 'visited': 0, 'matches': 0, 'state': 'progressing'},
            {'term': 'term #2', 'total': 2, 'visited': 0, 'matches': 0, 'state': 'progressing'}
        ])
        self.assertEqual(search_stat_entity.searches, [
            {'term': 'term #1', 'url': 'url1', 'page': 1, 'position': 1, 'visited': False},
            {'term': 'term #1', 'url': 'url2', 'page': 1, 'position': 2, 'visited': False},
            {'term': 'term #2', 'url': 'url3', 'page': 1, 'position': 1, 'visited': False},
            {'term': 'term #2', 'url': 'url4', 'page': 1, 'position': 2, 'visited': False}
        ])
