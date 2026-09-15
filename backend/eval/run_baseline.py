"""Baseline v1 — قياس فقط، صفر تغيير في الاسترجاع أو التوليد أو التقييم.

يقيس: Retrieval (recall@1/3/5 على السياق النهائي) + Generation
(faithfulness/relevance مع حالة التقييم) + Operational (latency).
الارتباط بالبناء لا بالبحث في السجلات: كل سجل يُبنى من قيم الإرجاع
لنفس الاستدعاء (hits + trace + زمن القياس).

ملاحظتان موثقتان:
- candidate-pool مقابل final-context غير قابلين للفصل دون تعديل loop.py
  (الـ trace يحمل أعداداً لا مفاتيح) — يُقاس السياق النهائي فقط الآن.
- doc_key تجزئة md5 غير قابلة للصيانة البشرية — المطابقة بالاسم+الصفحة،
  وتُدعم doc_key الدقيقة عند توفرها.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

EVAL_DIR = Path(__file__).resolve().parent
RESULTS_DIR = EVAL_DIR / "results"
KS = (1, 3, 5, 8)


def match_ref(hit: dict, ref: dict, expected_keys: list) -> bool:
    """مطابقة ضربة واحدة لمرجع متوقع: doc_key الدقيقة أولاً ثم الاسم+الصفحة."""
    if not isinstance(hit, dict):
        return False
    if expected_keys and hit.get("doc_key") in expected_keys:
        return True
    if ref.get("doc_key") and hit.get("doc_key") == ref["doc_key"]:
        return True
    want_file = (ref.get("file") or "").strip()
    if not want_file or want_file not in str(hit.get("doc_path") or "").replace("\\", "/"):
        return False
    # تسامح ±2 صفحة: المقاطع ~700 token فقد يجاور الصحيح (موثق، لا إخفاء)
    want_page = str(ref.get("page") or "").strip()
    if want_page:
        try:
            if abs(int(float(str(hit.get("page") or "0"))) - int(float(want_page))) > 2:
                return False
        except ValueError:
            if want_page not in str(hit.get("page") or ""):
                return False
    return True


def recall_at_k(hits: list, refs: list, expected_keys: list, k: int) -> float | None:
    """نسبة المراجع المتوقعة الموجودة في أول k نتائج. None بلا ground truth."""
    if not refs and not expected_keys:
        return None
    targets = list(refs)
    if expected_keys:
        targets = targets + [{"doc_key": dk} for dk in expected_keys]
    if not targets:
        return None
    top = (hits or [])[:k]
    found = 0
    for ref in targets:
        keys = [ref["doc_key"]] if ref.get("doc_key") else expected_keys
        if any(match_ref(h, ref, keys) for h in top):
            found += 1
    return found / len(targets)


def empty_metrics() -> dict:
    return {
        "cases": 0, "with_ground_truth": 0, "expects_no_context": 0,
        "recall": {f"recall@{k}": None for k in KS},
        "faithfulness_avg": None, "relevance_avg": None,
        "evaluated": 0, "eval_failed": 0, "eval_skipped": 0,
        "latency_ms_avg": None, "hits_count_avg": None, "modes": {},
    }


def aggregate(cases: list) -> dict:
    """تجميع المقاييس: المتوسطات على الناجح فقط، والفشل مُحصى لا مُخفى."""
    m = empty_metrics()
    m["cases"] = len(cases)
    rec_sum = {k: 0.0 for k in KS}
    rec_n = 0
    faith_sum = relev_sum = 0.0
    lat_sum = hits_sum = 0.0
    lat_n = hits_n = 0
    for c in cases:
        if c.get("expects_context") is False:
            m["expects_no_context"] += 1
        r = c.get("recall") or {}
        if r.get("has_ground_truth"):
            m["with_ground_truth"] += 1
            rec_n += 1
            for k in KS:
                rec_sum[k] += r.get(f"recall@{k}", 0.0) or 0.0
        st = (c.get("evaluation") or {}).get("status")
        if st == "success":
            m["evaluated"] += 1
            faith_sum += c["evaluation"]["faithfulness"]
            relev_sum += c["evaluation"]["relevance"]
        elif st == "failed":
            m["eval_failed"] += 1
        else:
            m["eval_skipped"] += 1
        if c.get("latency_ms") is not None:
            lat_sum += c["latency_ms"]
            lat_n += 1
        if c.get("hits_count") is not None:
            hits_sum += c["hits_count"]
            hits_n += 1
        mode = c.get("retrieval_mode") or "unknown"
        m["modes"][mode] = m["modes"].get(mode, 0) + 1
    if rec_n:
        m["recall"] = {f"recall@{k}": round(rec_sum[k] / rec_n, 3) for k in KS}
    if m["evaluated"]:
        m["faithfulness_avg"] = round(faith_sum / m["evaluated"], 3)
        m["relevance_avg"] = round(relev_sum / m["evaluated"], 3)
    if lat_n:
        m["latency_ms_avg"] = round(lat_sum / lat_n, 1)
    if hits_n:
        m["hits_count_avg"] = round(hits_sum / hits_n, 2)
    return m


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=BACKEND.parent, text=True).strip()
    except Exception:
        return "unknown"


class FakeStore:
    """مخزن مؤقت هرمسي: القياس لا يلوث المحادثات الحقيقية."""

    def __init__(self):
        self._threads: dict[int, list] = {}
        self._next = 1

    def thread_exists(self, tid: int) -> bool:
        return tid in self._threads

    def recent_history(self, tid: int | None) -> list:
        return []

    def create_thread(self, title=None) -> dict:
        tid = self._next
        self._next += 1
        self._threads[tid] = []
        return {"id": tid}

    def add_message(self, tid, role, content, sources=None) -> None:
        self._threads.setdefault(tid, []).append({"role": role})

    def get_messages(self, tid: int) -> list:
        return self._threads.get(tid, [])


def evaluate_answer(client, question: str, answer: str, hits: list) -> dict:
    """تقييم Ragas مع حالة صريحة: success/failed/skipped — لا متوسطات على الفشل."""
    if client is None:
        return {"status": "skipped", "faithfulness": None, "relevance": None, "reason": "no-client"}
    try:
        from app.evaluation.ragas import evaluate
        scores = evaluate(client, question, answer, hits)
        return {
            "status": "success",
            "faithfulness": scores.get("faithfulness"),
            "relevance": scores.get("relevance"),
            "reason": (scores.get("reason") or "")[:120],
        }
    except Exception as e:
        return {"status": "failed", "faithfulness": None, "relevance": None, "reason": str(e)[:120]}


def run_case(service, case: dict, client, kb, store) -> dict:
    """تشغيل حالة واحدة: سجل المخرجات يُبنى من قيم الإرجاع (ارتباط بالبناء)."""
    qid = case["id"]
    question = case["question"]
    refs = case.get("expected_refs", [])
    keys = case.get("expected_doc_keys", [])
    start = time.perf_counter()
    try:
        import asyncio
        result = asyncio.run(service.handle(question, None, client, kb, store, teacher_id="baseline"))
    except Exception as e:
        return {"id": qid, "category": case.get("category"), "question": question,
                "outcome": "error", "error": str(e)[:150], "latency_ms": round((time.perf_counter() - start) * 1000, 1)}
    latency = round((time.perf_counter() - start) * 1000, 1)
    if not isinstance(result, dict) or "answer" not in result:
        return {"id": qid, "category": case.get("category"), "question": question,
                "outcome": "clarification", "latency_ms": latency,
                "evaluation": {"status": "skipped", "reason": "clarification"}}
    hits = result.get("hits", []) or []
    answer = result.get("answer", "")
    rec = {f"recall@{k}": recall_at_k(hits, refs, keys, k) for k in KS}
    rec["has_ground_truth"] = bool(refs or keys)
    evaluation = evaluate_answer(client, question, answer, hits)
    mode = (hits[0].get("retrieval_mode", "") if hits else "")
    top_hits = [
        {"doc_path": str(h.get("doc_path") or "")[-80:], "page": h.get("page"),
         "title": str(h.get("title") or "")[:60], "mode": h.get("retrieval_mode", "")}
        for h in (hits or [])[:8] if isinstance(h, dict)
    ]
    return {
        "id": qid, "category": case.get("category"), "question": question,
        "outcome": "answered", "expects_context": case.get("expects_context", True),
        "hits_count": len(hits), "retrieval_mode": mode,
        "recall": rec, "evaluation": evaluation, "latency_ms": latency,
        "top_hits": top_hits,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Baseline v1 — قياس فقط")
    ap.add_argument("--questions", default=str(EVAL_DIR / "questions.json"))
    ap.add_argument("--limit", type=int, default=0, help="تشغيل أول N حالات فقط (0=الكل)")
    ap.add_argument("--check", action="store_true", help="فحص البيئة فقط بلا تشغيل")
    ap.add_argument("--no-eval", action="store_true", help="تخطي Ragas (توفير الحصة)")
    args = ap.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    commit = git_commit()
    cases_in = json.loads(Path(args.questions).read_text(encoding="utf-8"))["cases"]
    if args.limit:
        cases_in = cases_in[:args.limit]

    client = None
    kb = None
    if not args.check:
        from google import genai
        from app.knowledge.base import KnowledgeBase
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            print("GEMINI_API_KEY مفقود — شغل --check للفحص أو جهز المفتاح")
            return 2
        client = genai.Client(api_key=api_key)
        kb = KnowledgeBase()
        print(f"KB chunks: {kb.vector_service.count()}")
    else:
        try:
            from app.knowledge.base import KnowledgeBase
            print(f"KB chunks: {KnowledgeBase().vector_service.count()}")
        except SystemExit as e:
            print(f"KB غير مفهرسة: {e}")
            return 2
        print(f"GEMINI_API_KEY: {'موجود' if os.getenv('GEMINI_API_KEY') else 'مفقود'}")
        print(f"cases: {len(cases_in)} commit: {commit}")
        return 0

    from app.modules.chat.service import ChatService
    import app.modules.chat.service as chat_module
    from app.core.logging import setup_logging
    setup_logging()  # سطور retrieval.jsonl التشغيلية تُكتب أثناء القياس
    chat_module._update_teacher_memory = lambda *a, **k: None  # القياس لا يكتب ذاكرة حقيقية
    service = ChatService()
    store = FakeStore()
    if args.no_eval:
        client = None

    out_cases = []
    for case in cases_in:
        print(f"[{case['id']}] {case['question'][:50]} ...")
        out_cases.append(run_case(service, case, client, kb, store))

    snapshot = {
        "baseline_version": "v1",
        "commit": commit,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "question_count": len(out_cases),
        "config": {"recall_ks": list(KS), "top_kept": 8, "eval": "ragas-gemini",
                   "matcher": "file-basename+page±2",
                   "candidate_vs_final": "final-only (trace يحمل أعداداً لا مفاتيح)"},
        "metrics": aggregate(out_cases),
        "cases": out_cases,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = RESULTS_DIR / f"baseline_{commit}_{stamp}.json"
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(snapshot["metrics"], ensure_ascii=False, indent=1))
    print(f"saved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
