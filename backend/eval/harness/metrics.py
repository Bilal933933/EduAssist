"""المقاييس — دقة النية والتوجيه ومعدل استدعاء النموذج."""
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def summarize(results: list) -> dict:
    """يجمع النتائج الخام في ملخص واحد."""
    total = len(results)
    if not total:
        return {"cases": 0}
    correct = sum(1 for r in results if r.get("correct"))
    llm_calls = sum(1 for r in results if r.get("source") == "llm")
    ambiguous = sum(1 for r in results if r.get("ambiguous"))
    lat = [r.get("latency_ms", 0) for r in results]
    errors = [r for r in results if not r.get("correct")]
    agreements = [float(r.get("agreement", 1.0)) for r in results]
    unstable = sum(1 for a in agreements if a < 1.0)

    by_intent: dict = {}
    for r in results:
        key = r.get("expected") or "unknown"
        slot = by_intent.setdefault(key, {"total": 0, "correct": 0})
        slot["total"] += 1
        if r.get("correct"):
            slot["correct"] += 1
    for slot in by_intent.values():
        slot["accuracy"] = round(slot["correct"] / slot["total"], 3) if slot["total"] else 0.0

    return {
        "cases": total,
        "accuracy": round(correct / total, 3),
        "correct": correct,
        "wrong": total - correct,
        "llm_call_rate": round(llm_calls / total, 3),
        "llm_calls": llm_calls,
        "ambiguous_rate": round(ambiguous / total, 3),
        "latency_ms_avg": round(sum(lat) / len(lat), 1) if lat else 0.0,
        "agreement_avg": round(sum(agreements) / len(agreements), 3) if agreements else 1.0,
        "unstable_cases": unstable,
        "repeats": results[0].get("repeats", 1) if results else 1,
        "by_intent": by_intent,
        "errors": [
            {"id": e["id"], "question": e["question"], "expected": e["expected"], "predicted": e["predicted"], "source": e["source"]}
            for e in errors
        ],
    }
