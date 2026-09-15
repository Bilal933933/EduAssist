"""ترتيب FlashRank المحلي (offline بلا حصة) — ضعيف عربياً، باقٍ كطبقة وسطى."""
import threading
import time

from app.agent.reranker.shared import RETRY_COOLDOWN, small_pool

# متعدد اللغة أولاً للعربية؛ None = الافتراضي
_LOCAL_MODEL_NAMES = ("ms-marco-MultiBERT-L-12", None)
# مهلة بناء النموذج داخل الطلب (التنزيل بطيء لمرة واحدة)
_BUILD_TIMEOUT = 25
_ranker = None
_ranker_failed_at = 0.0
_holder = {}


def _build(name):
    try:
        from flashrank import Ranker
        _holder[name or "default"] = Ranker(model_name=name) if name else Ranker()
    except Exception as e:
        _holder[name or "default"] = e


def _local_ranker():
    """Ranker واحد مشترك؛ None عند التعذر (يسقط للطبقة التالية)."""
    global _ranker, _ranker_failed_at
    if _ranker is not None:
        return _ranker
    if time.time() - _ranker_failed_at < RETRY_COOLDOWN:
        return None
    _holder.clear()
    name = _LOCAL_MODEL_NAMES[0]
    t = threading.Thread(target=_build, args=(name,), daemon=True)
    t.start()
    t.join(_BUILD_TIMEOUT)
    if not t.is_alive():
        got = _holder.get(name or "default")
        if got is not None and not isinstance(got, Exception):
            _ranker = got
            print(f"[Rerank] نموذج محلي: {name}")
            return _ranker
        print(f"[Rerank] تعذر {name}: {got}")
    else:
        print("[Rerank] بناء النموذج تجاوز المهلة — heuristic fallback مؤقتاً")
    _ranker_failed_at = time.time()
    return None


def rerank_local(question: str, hits: list, top_k: int = 10) -> list | None:
    """ترتيب محلي offline بلا حصة. يعيد None عند التعذر ليسقط للطبقة التالية."""
    sp = small_pool(hits, top_k)
    if sp is not None:
        return sp
    ranker = _local_ranker()
    if ranker is None:
        return None
    try:
        from flashrank import RerankRequest
        passages = [
            {"id": i, "text": f"{h.get('title') or ''} | {(h.get('text') or '')[:500]}"}
            for i, h in enumerate(hits)
        ]
        res = ranker.rerank(RerankRequest(query=question or "", passages=passages))
        return [hits[r["id"]] for r in res[:top_k] if 0 <= r["id"] < len(hits)]
    except Exception as e:
        print(f"[Rerank local skip: {e}]")
        return None
