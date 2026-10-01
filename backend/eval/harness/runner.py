"""العداء المعزول — نفس الحالات لكل محول مع قياس الزمن والثبات."""
import os
import sys
import time
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _single_run(adapter_fn, question, ctx, client):
    try:
        return adapter_fn(question, ctx, client)
    except TypeError:
        return adapter_fn(question, ctx)


def run_all(adapter_fn, cases: list, client=None, repeats: int = 3, pin_model: str | None = None) -> list:
    """يشغل كل الحالات على محول واحد — يعيد نتائج خام مع ثبات التكرار.

    - repeats=1 يحافظ على السلوك القديم؛ repeats=3 يكشف عشوائية LLM.
    - pin_model يثبت GEMINI_PIN_MODEL أثناء التشغيل لمنع fallback العشوائي.
    - client=None (القواعد فقط) حتمي — تكرار واحد يكفي.
    """
    repeats = max(1, int(repeats or 1))
    if client is None:
        repeats = 1
    prev_pin = os.getenv("GEMINI_PIN_MODEL", "")
    try:
        if pin_model:
            os.environ["GEMINI_PIN_MODEL"] = pin_model
        results = []
        for case in cases:
            q = case["question"]
            ctx = case.get("context") or {}
            preds: list = []
            confs: list = []
            sources: list = []
            latencies: list = []
            error = None
            ambiguous = False
            for _ in range(repeats):
                start = time.perf_counter()
                try:
                    out = _single_run(adapter_fn, q, ctx, client)
                    latencies.append(round((time.perf_counter() - start) * 1000, 1))
                    preds.append(out.get("intent"))
                    confs.append(float(out.get("confidence", 0.0) or 0.0))
                    sources.append(out.get("source", ""))
                    ambiguous = bool(out.get("ambiguous", False))
                except Exception as e:
                    latencies.append(round((time.perf_counter() - start) * 1000, 1))
                    preds.append(None)
                    confs.append(0.0)
                    sources.append("error")
                    error = str(e)[:150]
            # التصويت بالأغلبية + نسبة الاتفاق كمقياس ثبات
            vote = Counter(preds).most_common(1)[0][0] if preds else None
            agreement = round(preds.count(vote) / len(preds), 3) if preds else 0.0
            results.append({
                "id": case["id"],
                "question": q,
                "expected": case["expected_intent"],
                "ambiguous_expected": case.get("ambiguous_expected", False),
                "predicted": vote,
                "predictions": preds,
                "agreement": agreement,
                "confidence": round(sum(confs) / len(confs), 3) if confs else 0.0,
                "source": Counter(sources).most_common(1)[0][0] if sources else "",
                "ambiguous": ambiguous,
                "correct": vote == case["expected_intent"],
                "latency_ms": round(sum(latencies) / len(latencies), 1) if latencies else 0.0,
                "repeats": repeats,
                "error": error,
            })
        return results
    finally:
        if pin_model:
            if prev_pin:
                os.environ["GEMINI_PIN_MODEL"] = prev_pin
            else:
                os.environ.pop("GEMINI_PIN_MODEL", None)
