import re
import json
import threading
import time

# نماذج FlashRank المرشحة (متعدد اللغة أولاً للعربية)
_LOCAL_MODEL_NAMES = ("ms-marco-MultiBERT-L-12", None)
# مهلة بناء النموذج داخل الطلب + تهدئة قبل إعادة المحاولة (التنزيل بطيء لمرة واحدة)
_BUILD_TIMEOUT = 25
_RETRY_COOLDOWN = 900
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
    """Ranker واحد مشترك؛ None عند التعذر (يُستخدم LLM fallback).

    البناء في خيط خلفي بمهلة: عند انتهائها يُستخدم LLM ويستمر التنزيل
    في الخلفية لمرة واحدة، وتُعاد المحاولة بعد تهدئة.
    """
    global _ranker, _ranker_failed_at
    if _ranker is not None:
        return _ranker
    if time.time() - _ranker_failed_at < _RETRY_COOLDOWN:
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
        print("[Rerank] بناء النموذج تجاوز المهلة — LLM fallback مؤقتاً")
    _ranker_failed_at = time.time()
    return None


def rerank_local(question: str, hits: list, top_k: int = 10) -> list | None:
    """ترتيب محلي offline بلا حصة. يعيد None عند التعذر ليتدخل LLM."""
    if len(hits) <= 3:
        return hits[:top_k]
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

RERANK_PROMPT = """رتب هذه المقتطفات حسب صلة مباشرة بسؤال المدرس.

سؤال المدرس: "{question}"

المقتطفات:
{chunks}

أجب JSON فقط:
{{"ranking": [3, 1, 5, 2, ...]}}
حيث الأرقام هي فهارس المقتطفات من الأكثر صلة للأقل. أعد الكل مرتباً.
"""


def rerank_llm(client, question: str, hits: list, top_k: int = 10) -> list:
    """يعيد ترتيب candidate pool: محلي أولاً (بلا حصة)، ثم LLM عند التعذر."""
    if len(hits) <= 3:
        return hits[:top_k]

    local = rerank_local(question, hits, top_k)
    if local is not None:
        print(f"[Rerank] محلي: {len(hits)} → {len(local)}")
        return local

    rows = []
    for i, h in enumerate(hits):
        meta = " | ".join(
            x for x in [
                f"المصدر: {h.get('source') or 'غير محدد'}",
                f"الصف: {h.get('grade') or 'عام'}",
                f"المادة: {h.get('subject') or 'غير محددة'}",
                f"الوحدة: {h.get('unit') or '-'}",
                f"الدرس: {h.get('lesson') or h.get('title') or '-'}",
                f"الصفحة: {h.get('page') or '-'}",
            ]
            if x
        )
        text = (h.get("text") or "")[:700]
        rows.append(f"{i+1}. [{meta}]\n{text}")

    chunks_text = "\n\n".join(rows)
    prompt = RERANK_PROMPT.format(question=question, chunks=chunks_text)

    try:
        from app.agent.fc_client import call_simple
        raw = call_simple(client, prompt, "أنت مرتب. أجب JSON فقط.")
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return hits[:top_k]
        data = json.loads(m.group())
        ranking = data.get("ranking", list(range(1, len(hits) + 1)))
        ranked = []
        seen = set()
        for idx in ranking:
            if 1 <= idx <= len(hits) and idx not in seen:
                ranked.append(hits[idx - 1])
                seen.add(idx)
        for idx, h in enumerate(hits, start=1):
            if idx not in seen:
                ranked.append(h)
        print(f"[Rerank] {len(hits)} → {len(ranked[:top_k])} مرتب")
        return ranked[:top_k]
    except Exception as e:
        print(f"[Rerank skip: {e}]")
        return hits[:top_k]
