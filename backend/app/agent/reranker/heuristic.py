"""ترتيب حتمي بلا أي نموذج أو تنزيل: دمج الإشارات الموحدة + تطابق عربي.

يعمل دائماً (offline صرف) — شبكة الأمان قبل LLM. يستخدم نفس تطبيع
lexical الحالي، فيرث جودته العربية بدل منافستها.
"""
import os

from app.agent.reranker.shared import small_pool

# الأوزان مضبوطة يدوياً لا مقاسة — تُعاير عبر eval/run_baseline.py عند توفر بيانات
_W_RRF = 0.45
_W_SIM = 0.25
_W_LEX = 0.15
_W_TITLE = 0.10
_W_CONCEPT = 0.05


def prefer_first() -> bool:
    """RERANK_HEURISTIC_FIRST=1 يقدّم heuristic على FlashRank (مفيد بلا BGE)."""
    return os.getenv("RERANK_HEURISTIC_FIRST", "0") == "1"


def _tok_set(texts, extract, strip_al) -> set:
    out = set()
    for tx in texts:
        if not tx:
            continue
        if isinstance(tx, list):
            tx = " ".join(tx)
        toks = extract(str(tx), filter_stopwords=False)
        out.update(toks)
        out.update(strip_al(t) for t in toks)
    return out


def rerank_heuristic(question: str, hits: list, top_k: int = 10) -> list:
    sp = small_pool(hits, top_k)
    if sp is not None:
        return sp
    try:
        from app.knowledge.search import _extract_tokens, _strip_al
    except Exception:
        return hits[:top_k]
    try:
        q_tokens = _extract_tokens(question or "") or _extract_tokens(question or "", filter_stopwords=False)
        q_set = set(q_tokens) | {_strip_al(t) for t in q_tokens}
        if not q_set:
            return hits[:top_k]
        rrf_max = max([float(h.get("rrf_score", 0.0) or 0.0) for h in hits] + [1e-9])
        lex_max = max([float(h.get("lexical_score", 0.0) or 0.0) for h in hits] + [1e-9])

        scored = []
        for idx, h in enumerate(hits):
            title_set = _tok_set((h.get("title"), h.get("lesson")), _extract_tokens, _strip_al)
            concept_set = _tok_set((h.get("concepts"),), _extract_tokens, _strip_al)
            text_set = _tok_set(((h.get("text") or "")[:700],), _extract_tokens, _strip_al)
            n = max(len(q_set), 1)
            title_hit = len(q_set & title_set) / n
            concept_hit = len(q_set & concept_set) / n
            text_hit = len(q_set & text_set) / n
            score = (
                _W_RRF * (float(h.get("rrf_score", 0.0) or 0.0) / rrf_max)
                + _W_SIM * float(h.get("similarity", 0.0) or 0.0)
                + _W_LEX * (float(h.get("lexical_score", 0.0) or 0.0) / lex_max)
                + _W_TITLE * min(title_hit * 2.0, 1.0)
                + _W_CONCEPT * min((concept_hit + text_hit) * 2.0, 1.0)
            )
            scored.append((score, idx))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [hits[i] for _, i in scored[:top_k]]
    except Exception as e:
        print(f"[Rerank heuristic skip: {e}]")
        return hits[:top_k]
