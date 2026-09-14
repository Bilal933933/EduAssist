import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.logging import get_logger, setup_logging
from app.core.request_context import get_request_id_ctx, set_request_id
from app.knowledge.retrieval_log import log_retrieval, summarize_hits


def test_request_id_roundtrip():
    set_request_id("abc123")
    assert get_request_id_ctx() == "abc123"
    set_request_id(None)


def test_retrieval_line_is_jsonl(tmp_path, monkeypatch):
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    import app.core.logging as L
    L._configured = False
    setup_logging(log_dir=str(tmp_path))
    set_request_id("rid-1")
    hits = [{"doc_key": "k1", "title": "الفاعل", "lexical_score": 2.0, "similarity": 0.9, "retrieval_mode": "lexical_only"}]
    log_retrieval("حضر درس الفاعل", hits, scope={"grade": "grade5"}, mode="lexical_only", latency_ms=12.3, route="chat", thread_id=7)
    line = (tmp_path / "retrieval.jsonl").read_text(encoding="utf-8").strip().splitlines()[-1]
    payload = json.loads(line)
    assert payload["type"] == "retrieval"
    assert payload["hits_count"] == 1
    assert payload["hits"][0]["doc_key"] == "k1"
    assert payload["thread_id"] == 7
    assert summarize_hits(None) == []
    set_request_id(None)


def test_no_secret_leak(tmp_path, monkeypatch):
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSECRET1234567890")
    import app.core.logging as L
    L._configured = False
    setup_logging(log_dir=str(tmp_path))
    logger = get_logger("errors")
    logger.warning("failed with AIzaSECRET1234567890 and key=AIzaSECRET1234567890")
    content = "".join((tmp_path / f).read_text(encoding="utf-8") for f in ("errors.jsonl",) if (tmp_path / f).exists())
    assert "AIzaSECRET" not in content
    assert "[REDACTED]" in content
