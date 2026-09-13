import sys
sys.stdout.reconfigure(encoding='utf-8')

from unittest.mock import MagicMock, patch
from src.agent.decomposer import decompose_question
from src.agent.validator import validate_citations

def test_decomposer_prepare_lesson():
    client = MagicMock()
    # mock _call_simple ليعيد JSON تفكيك
    with patch("src.agent.fc_client.call_simple", return_value='{"queries": ["تعريف الفاعل", "علامات رفع الفاعل"]}'):
        queries = decompose_question(client, "حضر لي درس الفاعل - الصف الخامس")
        assert len(queries) >= 2
        assert any("الفاعل" in q for q in queries)

def test_decomposer_short():
    client = MagicMock()
    queries = decompose_question(client, "ما هو المبتدأ؟")
    # سؤال قصير عادي → لا يفكك كثيراً
    assert len(queries) >= 1

def test_validator_correct():
    client = MagicMock()
    # mock _call_simple ليعيد valid=true
    with patch("src.agent.fc_client.call_simple", return_value='{"valid": true, "issues": [], "corrected": "نص صحيح"}'):
        valid, corrected, issues = validate_citations(client, "الفاعل مرفوع", [{"title": "ت", "text": "الفاعل مرفوع"}])
        assert valid == True

def test_validator_hallucination():
    client = MagicMock()
    with patch("src.agent.fc_client.call_simple", return_value='{"valid": false, "issues": ["هلوسة"], "corrected": "لا يوجد في مصادرك"}'):
        valid, corrected, issues = validate_citations(client, "هلوسة", [{"title": "ت", "text": "نص"}])
        assert valid == False
        assert "لا يوجد" in corrected

def test_chat_store():
    from src.storage.chat_store import ChatStore
    import tempfile, os
    assert ChatStore is not None
