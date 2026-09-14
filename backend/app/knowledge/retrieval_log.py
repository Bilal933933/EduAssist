"""تسجيل الاسترجاع — سطر JSONL واحد لكل سؤال (الأهم للتحسين).

يُستدعى من طبقة التطبيق فقط (ChatService/CardsService)، لا من src/.
السؤال والعناوين مقتطعة عمداً لتقليل الحجم ومنع التسرب.
"""
import json
import time

from app.core.logging import get_logger

TOP_KEPT = 8
QUESTION_LOG_LEN = 120
TITLE_LOG_LEN = 80


def summarize_hits(hits: list | None, limit: int = TOP_KEPT) -> list[dict]:
    out: list[dict] = []
    for rank, h in enumerate((hits or [])[:limit]):
        if not isinstance(h, dict):
            continue
        out.append({
            "rank": rank,
            "doc_key": str(h.get("doc_key", ""))[:64],
            "title": str(h.get("title", ""))[:TITLE_LOG_LEN],
            "lexical": float(h.get("lexical_score", 0.0) or 0.0),
            "similarity": float(h.get("similarity", 0.0) or 0.0),
            "mode": h.get("retrieval_mode", ""),
        })
    return out


def log_retrieval(
    question: str,
    hits: list | None,
    scope: dict | None = None,
    mode: str = "",
    latency_ms: float = 0.0,
    route: str = "chat",
    thread_id: int | None = None,
    case_id: str | None = None,
    faithfulness: float | None = None,
    relevance: float | None = None,
    evaluation_status: str | None = None,
) -> None:
    """يكتب سطر retrieval.jsonl واحد. لا يرفع استثناء أبداً (التسجيل ثانوي).

    حقول التقييم اختيارية لربط حدث الاسترجاع بنتيجته بنفس المعرف (case_id)
    دون جعل اللوجر stateful: المتصل يمرر القيم الجاهزة فقط.
    """
    try:
        payload = {
            "type": "retrieval",
            "ts": time.time(),
            "route": route,
            "thread_id": thread_id,
            "question": (question or "")[:QUESTION_LOG_LEN],
            "scope": scope or {},
            "mode": mode,
            "latency_ms": round(float(latency_ms or 0.0), 1),
            "hits_count": len(hits or []),
            "hits": summarize_hits(hits),
        }
        if case_id is not None:
            payload["case_id"] = case_id
        if evaluation_status is not None:
            payload["evaluation_status"] = evaluation_status
        if faithfulness is not None:
            payload["faithfulness"] = faithfulness
        if relevance is not None:
            payload["relevance"] = relevance
        get_logger("retrieval").info(json.dumps(payload, ensure_ascii=False))
    except Exception:
        pass
