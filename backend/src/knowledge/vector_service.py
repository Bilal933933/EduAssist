import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from src.knowledge.store import VectorStore
from src.knowledge.search import VectorSearch


class VectorService(VectorStore):
    """واجهة موحدة للتخزين والبحث."""
    def __init__(self, db_url=None):
        super().__init__(db_url)
        self._search = VectorSearch(self.Session)

    def search(self, query_embedding, top_k=10, query_text="", scope=None):
        return self._search.search(query_embedding, top_k, query_text=query_text, scope=scope)

    def lexical_search(self, query, top_k=10, scope=None):
        return self._search.lexical_search(query, top_k, scope=scope)
