from data.search_result import SearchResult
from typing import List
from collections import defaultdict

class SearchStatEntity():
    def __init__(self, scan_id, search_results: List[SearchResult]):
        self.scan_id = scan_id
        self.search_results = search_results
        self.stats = self._generate_stats()
        self.searches = self._generate_searches()
    
    def _generate_stats(self):
        term_counts = defaultdict(int)
        for result in self.search_results:
            term_counts[result.search_term] += 1
        
        stats_entries = []
        for term, total in term_counts.items():
            stats_entry = {
                'term': term,
                'total': total,
                'visited': 0,
                'matches': 0,
                'state': 'progressing'
            }
            stats_entries.append(stats_entry)
        return stats_entries
    
    def _generate_searches(self):
        searches = []
        for result in self.search_results:
            search_entry = {
                'term': result.search_term,
                'url': result.url,
                'page': result.page,
                'position': result.position,
                'visited': False
            }
            searches.append(search_entry)
        return searches
    
    def to_dict(self):
        return {
            'scanId': self.scan_id,
            'stats': self.stats,
            'searches': self.searches
        }



