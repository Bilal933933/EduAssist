from src.knowledge.vector_service import VectorService
from src.knowledge.hybrid import rrf_fuse
try:
    from app.agent import extract_scope, rerank_llm
except ImportError:  # توافقية أثناء الترحيل
    from app.modules.lesson_knowledge.application.agent.clarifier import extract_scope
    from app.modules.lesson_knowledge.application.agent.reranker import rerank_llm

class RetrievalService:
    """Domain service — فصل retrieval عن HTTP و Agent. يستخدم scope filtering قبل التشابه."""

    def __init__(self, vector_service: VectorService | None = None):
        self.vs = vector_service or VectorService()

    def retrieve(self, question: str, query_vector: list | None = None, top_k: int = 8, scope: dict | None = None, client=None, embed_fn=None):
        resolved_scope = scope or extract_scope(question)
        candidate_k = 40
        lexical_hits = self.vs.lexical_search(question, top_k=candidate_k, scope=resolved_scope)
        max_lex = max((float(h.get("lexical_score", 0.0)) for h in lexical_hits), default=0.0)
        if len(lexical_hits) >= 3 and max_lex >= 1.4:
            fused = lexical_hits
            for hit in fused:
                hit["retrieval_mode"] = "lexical_only"
        else:
            if query_vector is None and embed_fn is not None:
                query_vector = embed_fn()
            if query_vector is None:
                fused = lexical_hits
                for hit in fused:
                    hit["retrieval_mode"] = "lexical_only"
            else:
                semantic_hits = self.vs.search(query_vector, top_k=candidate_k, query_text=question, scope=resolved_scope)
                fused = rrf_fuse(semantic_hits, lexical_hits, top_k=20, lexical_weight=1.0)
                for hit in fused:
                    hit["retrieval_mode"] = "hybrid_fallback"
        # reranker يرى 700 حرف + metadata
        if client and fused:
            try:
                fused = rerank_llm(client, question, fused, top_k=10)
            except Exception:
                fused = fused[:10]
        else:
            fused = fused[:10]
        # final context 8
        return fused[:top_k], resolved_scope

    def count(self) -> int:
        return self.vs.count()
