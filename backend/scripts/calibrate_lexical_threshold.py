"""معايرة عتبة البحث النصي (عربية فقط) على lexical_search الحالي."""
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent.clarifier import extract_scope
from src.knowledge.vector_service import VectorService


def run(queries_path: Path, out_path: Path, top_k: int) -> int:
    queries = json.loads(queries_path.read_text(encoding="utf-8"))
    vs = VectorService()
    try:
        total = vs.count()
    except Exception as exc:
        print(f"DB error: {exc}")
        print("تأكد من تشغيل PostgreSQL و VECTOR_DATABASE_URL")
        return 2
    print(f"chunks in DB: {total}")
    if total == 0:
        print("القاعدة فارغة: الفهرس أولا ثم أعد التشغيل")

    rows = []
    for q in queries:
        qid = q.get("id", "")
        question = q.get("question", "")
        scope = q.get("scope") or extract_scope(question)
        try:
            hits = vs.lexical_search(question, top_k=top_k, scope=scope)
        except Exception as exc:
            print(f"{qid} error: {exc}")
            hits = []
        max_score = float(hits[0].get("lexical_score", 0.0)) if hits else 0.0
        count_good = sum(1 for h in hits if float(h.get("lexical_score", 0.0)) > 0.5)
        top3 = [(h.get("title", ""), float(h.get("lexical_score", 0.0))) for h in hits[:3]]
        while len(top3) < 3:
            top3.append(("", 0.0))
        rows.append({
            "id": qid,
            "category": q.get("category", ""),
            "expected": q.get("expected", ""),
            "question": question,
            "max_score": round(max_score, 3),
            "count_good": count_good,
            "top1_title": top3[0][0][:80],
            "top1_score": round(top3[0][1], 3),
            "top2_title": top3[1][0][:80],
            "top2_score": round(top3[1][1], 3),
            "top3_title": top3[2][0][:80],
            "top3_score": round(top3[2][1], 3),
        })
        print(f"{qid} [{q.get('category')}] max={max_score:.3f} good={count_good} | {top3[0][0][:60]}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)
    print(f"saved: {out_path}")

    by_cat: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        by_cat[r["category"]].append(r["max_score"])
    print("--- avg max_score per category ---")
    for cat, vals in by_cat.items():
        avg = sum(vals) / len(vals) if vals else 0.0
        print(f"{cat}: n={len(vals)} avg={avg:.3f} min={min(vals) if vals else 0:.3f} max={max(vals) if vals else 0:.3f}")
    print("اقتراح أولي: قوي >= 1.4 | مقبول 1.0-1.4 | ضعيف < 1.0 (يعدل بعد بياناتك)")
    return 0


def main() -> None:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="معايرة عتبة lexical للعربية")
    parser.add_argument("--queries", default=str(base / "calibration_queries.json"))
    parser.add_argument("--out", default=str(base / "calibration_results.csv"))
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()
    raise SystemExit(run(Path(args.queries), Path(args.out), args.top_k))


if __name__ == "__main__":
    main()
