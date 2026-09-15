"""ترتيب BGE العربي (cross-encoder متعدد اللغات) — يتطلب تنزيل ~2GB لمرة واحدة."""
import os
import threading
import time

from app.agent.reranker.shared import RETRY_COOLDOWN, passage_text, small_pool

_BGE_MODEL_ID = os.getenv("RERANK_BGE_MODEL", "BAAI/bge-reranker-v2-m3")
_BGE_BATCH = 8
_bge = None
_bge_failed_at = 0.0
_bge_warming = False


def enabled() -> bool:
    return os.getenv("RERANK_BGE", "1") != "0"


def _load(local_only: bool):
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch
    kw = {"local_files_only": True} if local_only else {}
    tok = AutoTokenizer.from_pretrained(_BGE_MODEL_ID, **kw)
    model = AutoModelForSequenceClassification.from_pretrained(_BGE_MODEL_ID, **kw)
    model.eval()
    try:
        model = model.to(torch.device("cpu"))
    except Exception:
        pass
    return tok, model


def _warm():
    """تنزيل خلفي لمرة واحدة؛ يفعّل BGE للطلبات اللاحقة دون حجب الحالي."""
    global _bge, _bge_warming
    try:
        _bge = _load(local_only=False)
        print(f"[Rerank] نموذج BGE جاهز: {_BGE_MODEL_ID}")
    except Exception as e:
        print(f"[Rerank] تعذر تنزيل BGE: {e}")
    finally:
        _bge_warming = False


def _loader():
    """محمل كسول: الكاش داخل الطلب، وغيابه تنزيل خلفي بلا حجب — None للسقوط."""
    global _bge, _bge_failed_at, _bge_warming
    if not enabled():
        return None
    if _bge is not None:
        return _bge
    if time.time() - _bge_failed_at < RETRY_COOLDOWN:
        return None
    try:
        _bge = _load(local_only=True)
        print(f"[Rerank] نموذج BGE (كاش): {_BGE_MODEL_ID}")
        return _bge
    except Exception:
        pass
    if not _bge_warming:
        _bge_warming = True
        threading.Thread(target=_warm, daemon=True).start()
        print("[Rerank] BGE غير مخزن — بدأ التنزيل الخلفي، FlashRank مؤقتاً")
    _bge_failed_at = time.time()
    return None


def rerank_bge(question: str, hits: list, top_k: int = 10) -> list | None:
    """ترتيب cross-encoder عربي. يعيد None عند التعذر ليسقط للطبقة التالية."""
    sp = small_pool(hits, top_k)
    if sp is not None:
        return sp
    got = _loader()
    if got is None:
        return None
    try:
        import torch
        tok, model = got
        pairs = [(question or "", passage_text(h)) for h in hits]
        scores: list[float] = []
        with torch.no_grad():
            for i in range(0, len(pairs), _BGE_BATCH):
                batch = pairs[i:i + _BGE_BATCH]
                enc = tok([q for q, _ in batch], [p for _, p in batch],
                          truncation=True, max_length=512, padding=True, return_tensors="pt")
                logits = model(**enc).logits
                flat = logits.squeeze(-1).float().tolist()
                scores.extend(flat if isinstance(flat, list) else [flat])
        order = sorted(range(len(hits)), key=lambda i: -scores[i])
        return [hits[i] for i in order[:top_k]]
    except Exception as e:
        print(f"[Rerank BGE skip: {e}]")
        return None
