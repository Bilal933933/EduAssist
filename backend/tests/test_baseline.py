import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

import run_baseline as rb


def _hits():
    return [
        {"doc_key": "a1", "doc_path": "x/part-05.md", "page": "171", "title": "t"},
        {"doc_key": "b2", "doc_path": "y/part-11.md", "page": 439, "title": "t"},
        {"doc_key": "c3", "doc_path": "z/other.md", "page": "9", "title": "t"},
    ]


def test_match_doc_key_exact():
    assert rb.match_ref({"doc_key": "a1"}, {}, ["a1"]) is True
    assert rb.match_ref({"doc_key": "zz"}, {}, ["a1"]) is False


def test_match_file_page():
    assert rb.match_ref(_hits()[0], {"file": "part-05.md", "page": "171"}, []) is True
    assert rb.match_ref(_hits()[0], {"file": "part-05.md", "page": "999"}, []) is False
    assert rb.match_ref(_hits()[1], {"file": "part-11.md", "page": "439"}, []) is True
    assert rb.match_ref(_hits()[2], {"file": "part-05.md"}, []) is False


def test_page_tolerance():
    hit = {"doc_key": "x", "doc_path": "references/general/كتاب/part-05.md", "page": 170}
    assert rb.match_ref(hit, {"file": "part-05.md", "page": "171"}, []) is True
    assert rb.match_ref(hit, {"file": "part-05.md", "page": "175"}, []) is False
    assert rb.match_ref(hit, {"file": "part-09.md", "page": "170"}, []) is False


def test_recall_at_k():
    refs = [{"file": "part-05.md", "page": "171"}, {"file": "part-11.md", "page": "439"}]
    assert rb.recall_at_k(_hits(), refs, [], 1) == 0.5
    assert rb.recall_at_k(_hits(), refs, [], 2) == 1.0
    assert rb.recall_at_k(_hits(), refs, [], 8) == 1.0
    assert rb.recall_at_k(_hits(), [], [], 8) is None


def test_aggregate_ignores_failed_evals():
    cases = [
        {"recall": {"recall@1": 1.0, "has_ground_truth": True},
         "evaluation": {"status": "success", "faithfulness": 0.8, "relevance": 0.9},
         "latency_ms": 100.0, "hits_count": 5, "retrieval_mode": "lexical_only"},
        {"recall": {"recall@1": 0.0, "has_ground_truth": True},
         "evaluation": {"status": "failed"},
         "latency_ms": 200.0, "hits_count": 3, "retrieval_mode": "hybrid_fallback"},
        {"recall": {"has_ground_truth": False},
         "evaluation": {"status": "skipped"},
         "latency_ms": 50.0, "hits_count": 0, "retrieval_mode": ""},
    ]
    m = rb.aggregate(cases)
    assert m["cases"] == 3
    assert m["with_ground_truth"] == 2
    assert m["recall"]["recall@1"] == 0.5
    assert m["faithfulness_avg"] == 0.8  # الفاشل لا يدخل المتوسط
    assert m["relevance_avg"] == 0.9
    assert m["evaluated"] == 1 and m["eval_failed"] == 1 and m["eval_skipped"] == 1
    assert m["latency_ms_avg"] == round(350 / 3, 1)
    assert m["modes"] == {"lexical_only": 1, "hybrid_fallback": 1, "unknown": 1}


def test_questions_distribution():
    import json
    qs = json.loads((Path(__file__).resolve().parents[1] / "eval" / "questions.json").read_text(encoding="utf-8"))["cases"]
    assert len(qs) == 20
    from collections import Counter
    cats = Counter(c["category"] for c in qs)
    assert cats == {"direct": 5, "paraphrase": 4, "multi_chunk": 4, "short": 3, "semantic": 2, "lexical": 2}
    assert all(c.get("id") and c.get("question") for c in qs)
    assert sum(1 for c in qs if c.get("expects_context") is False) == 1
