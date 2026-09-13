import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from src.knowledge.vector_service import VectorService
from src.knowledge.hybrid import rrf_fuse
from src.agent.clarifier import extract_scope

load_dotenv()


class KnowledgeBase:
    """قاعدة المعرفة: scope filtering ثم candidate retrieval ثم RRF."""

    def __init__(self):
        self.vector_service = VectorService()
        if self.vector_service.count() == 0:
            raise SystemExit("المتجهات غير مفهرسة. شغّل: python src/indexer.py أولاً")

    def search(self, query_vector, top_k=10, query_text="", scope=None):
        return self.vector_service.search(query_vector, top_k, query_text=query_text, scope=scope)

    def hybrid_search(
        self,
        question,
        query_vector=None,
        top_k=8,
        scope=None,
        candidate_k=40,
        fused_k=20,
        embed_fn=None,
    ):
        """Cascade retrieval: lexical أولاً، والتضمين والدلالي فقط عند الضعف."""
        resolved_scope = scope or extract_scope(question)
        candidate_k = max(int(candidate_k), 40)
        fused_k = max(int(fused_k), 20)
        lexical_hits = self.vector_service.lexical_search(
            question,
            top_k=candidate_k,
            scope=resolved_scope,
        )
        max_lex = max((float(h.get("lexical_score", 0.0)) for h in lexical_hits), default=0.0)
        if len(lexical_hits) >= 3 and max_lex >= 1.4:
            for hit in lexical_hits:
                hit["retrieval_scope"] = resolved_scope
                hit["retrieval_mode"] = "lexical_only"
            return lexical_hits[:max(1, int(top_k))]
        if query_vector is None:
            if embed_fn is None:
                for hit in lexical_hits:
                    hit["retrieval_scope"] = resolved_scope
                    hit["retrieval_mode"] = "lexical_only"
                return lexical_hits[:max(1, int(top_k))]
            query_vector = embed_fn()
        semantic_hits = self.search(
            query_vector,
            top_k=candidate_k,
            query_text=question,
            scope=resolved_scope,
        )
        fused = rrf_fuse(
            semantic_hits,
            lexical_hits,
            top_k=fused_k,
            lexical_weight=2.0,
        )
        for hit in fused:
            hit["retrieval_scope"] = resolved_scope
            hit["retrieval_mode"] = "hybrid_fallback"
        return fused[:max(1, int(top_k))]
