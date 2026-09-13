"""اختبارات بوابة الصلة (mock — بلا LLM)."""
import json
import sys
from unittest.mock import patch

sys.path.insert(0, ".")

from src.agent.critic import judge_relevance, judge_and_filter, _restore_floor


def _hits_branch(n, branch="نحو"):
    return [
        {"doc_key": f"k{i}", "title": f"عنوان {i}", "source": "مرجع",
         "branch": branch, "page": i, "text": f"نص {i} " * 20}
        for i in range(n)
    ]


def test_restore_floor_prefers_same_branch():
    hits = _hits_branch(3, "نحو") + _hits_branch(3, "بلاغة")
    for i, h in enumerate(hits[3:], start=3):
        h["doc_key"] = f"b{i}"
    kept = [hits[0]]
    verdict = {"drop": [1, 2, 3, 4, 5]}
    kept, restored = _restore_floor(hits, kept, verdict)
    assert len(kept) == 5, len(kept)
    assert restored == [1, 2, 3, 4], restored
    assert all("نحو" in str(hits[i].get("branch")) for i in restored[:2])


def _hits(n):
    return [
        {"doc_key": f"k{i}", "title": f"عنوان {i}", "source": "مرجع",
         "branch": "نحو", "page": i, "text": f"نص {i} " * 20}
        for i in range(n)
    ]


def _ok_json(keep):
    return json.dumps({"keep": keep, "drop": [], "missing": [],
                       "next_queries": [], "proceed": True})


def test_batch_merge_keeps_all():
    with patch("src.agent.fc_client.call_simple",
               side_effect=[_ok_json(list(range(0, 20))), _ok_json(list(range(20, 35)))]):
        v = judge_relevance(None, "سؤال", _hits(35))
    assert v["keep"] == list(range(35)), v["keep"]
    assert v["unjudged"] == 0
    assert len(v["kept_titles"]) == 35


def test_beyond_batch_counted_as_unjudged():
    with patch("src.agent.fc_client.call_simple",
               return_value=_ok_json(list(range(0, 20)))):
        v = judge_relevance(None, "سؤال", _hits(50))
    assert v["unjudged"] == 10 and v["keep"] == list(range(20)), (v["unjudged"], v["keep"])


def test_fail_open_on_llm_error():
    with patch("src.agent.fc_client.call_simple", side_effect=RuntimeError("429")):
        v = judge_relevance(None, "سؤال", _hits(5))
    assert v["keep"] == [0, 1, 2, 3, 4] and v["proceed"] is True


def test_retry_fires_once_then_keeps():
    first = json.dumps({"keep": [0], "drop": [1], "missing": ["الفاعل"],
                        "next_queries": ["تعريف الفاعل"], "proceed": False})
    second = json.dumps({"keep": [0, 1, 2], "drop": [], "missing": [],
                         "next_queries": [], "proceed": True})
    extra = [{"doc_key": "kx", "title": "إضافي", "source": "م",
              "branch": "نحو", "page": 1, "text": "نص إضافي"}]
    with patch("src.agent.fc_client.call_simple", side_effect=[first, second]), \
         patch("src.agent.tools.execute_tool", return_value=extra):
        kept, info = judge_and_filter(None, "سؤال", _hits(2), kb=None, scope={})
    assert info["retry"] is True and info["kept"] == 3, info
    assert len(info["dropped_titles"]) == 0
