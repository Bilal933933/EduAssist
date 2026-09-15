"""دمج نتائج البحث الدلالي والمعجمي عبر Reciprocal Rank Fusion."""


def _hit_key(hit: dict):
    # doc_key هو الهوية الأفضل بعد P0؛ fallback يحافظ على التوافق مع النتائج القديمة.
    return hit.get("doc_key") or (
        hit.get("source") or "",
        hit.get("page"),
        (hit.get("title") or "")[:120],
        (hit.get("text") or "")[:80],
    )


def rrf_fuse(semantic_hits, lexical_hits, top_k=20, k=60, lexical_weight=2.0):
    """40+40 candidates → RRF. لا توجد boosts أو تنويعات hard-coded بعد P0."""
    scores = {}
    hits = {}
    for ranked, weight in ((lexical_hits or [], lexical_weight), (semantic_hits or [], 1.0)):
        for rank, hit in enumerate(ranked):
            key = _hit_key(hit)
            hits.setdefault(key, hit)
            scores[key] = scores.get(key, 0.0) + weight * (1.0 / (k + rank + 1))

    fused = []
    for key, hit in hits.items():
        merged = dict(hit)
        merged["rrf_score"] = scores[key]
        fused.append(merged)

    # تطبيع similarity إلى [0,1]: الدرجة المعجمية خام وقد تتجاوز 1
    lex_max = max([float(h.get("lexical_score", 0.0)) for h in fused] + [1.0])
    for merged in fused:
        if "similarity" not in merged:
            merged["similarity"] = min(1.0, float(merged.get("lexical_score", 0.0)) / lex_max)
        else:
            try:
                merged["similarity"] = min(1.0, max(0.0, float(merged["similarity"])))
            except (TypeError, ValueError):
                merged["similarity"] = 0.0

    fused.sort(key=lambda h: -h["rrf_score"])
    return fused[:max(1, int(top_k))]
