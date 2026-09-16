import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from app.core.errors import AppError
from app.knowledge.vector_service import VectorService
from app.knowledge.hybrid import rrf_fuse
from app.agent.clarifier import extract_scope


class KnowledgeBase:
    """قاعدة المعرفة: scope filtering ثم candidate retrieval ثم RRF."""

    def __init__(self):
        self.vector_service = VectorService()
        if self.vector_service.count() == 0:
            raise AppError("KB_NOT_INDEXED")

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
        resolved_scope = dict(scope or extract_scope(question) or {})
        # بلا subject محلل: عربية افتراضياً (NULL تُعامل كعربية في _where_clause).
        # يمنع تسرب مواد أخرى (إنجليزية/علوم) لأسئلة بلا نطاق.
        if not resolved_scope.get("subject"):
            resolved_scope["subject"] = "اللغة العربية"
        candidate_k = max(int(candidate_k), 1)
        fused_k = max(int(fused_k), 1)
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

    def hybrid_search_pedagogy(
        self,
        question,
        query_vector=None,
        top_k=5,
        scope=None,
        candidate_k=20,
        fused_k=10,
        embed_fn=None,
    ):
        """Tier2 تربوي منفصل: source_type=pedagogy + فلتر grade/stage.

        يعيد [] بأمان عندما تكون كتب pedagogy غير مضافة بعد.
        لا يخلط مع Tier1 — الدمج يكون وسماً فقط عند العرض.
        """
        pedagogy_scope = dict(scope or {})
        pedagogy_scope["source_type"] = "pedagogy"
        try:
            hits = self.hybrid_search(
                question,
                query_vector,
                top_k=top_k,
                scope=pedagogy_scope,
                candidate_k=candidate_k,
                fused_k=fused_k,
                embed_fn=embed_fn,
            )
        except Exception:
            return []
        for hit in hits or []:
            hit["retrieval_mode"] = "pedagogy_tier2"
            hit["retrieval_scope"] = pedagogy_scope
        return hits or []
