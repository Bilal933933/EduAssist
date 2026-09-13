import sys
sys.stdout.reconfigure(encoding='utf-8')

from unittest.mock import MagicMock, patch

from app.modules.grammar_correction.application import correct_text_use_case as uc
from app.modules.grammar_correction.application.grammar_prompts import (
    GRAMMAR_SYSTEM,
)


def test_prompt_has_no_errors_guard():
    """حارس انحدار: سطر حالة لا-أخطاء إلزامي — بدونه يهلوس النموذج أخطاء وهمية."""
    assert "صحيحاً تماماً" in GRAMMAR_SYSTEM
    assert "لا تخترع أخطاء" in GRAMMAR_SYSTEM


def test_correct_text_uses_shared_client_and_prompt():
    client = MagicMock()
    with patch.object(uc, "call_simple", return_value="مصحح") as mocked:
        assert uc.correct_text(client, "نص فيه خطأ") == "مصحح"
        mocked.assert_called_once()
        args = mocked.call_args[0]
        assert args[0] is client
        assert args[2] == GRAMMAR_SYSTEM


def test_result_contract_matches_lesson_shape():
    result = uc.build_grammar_result("جواب", thread_id=7)
    assert result["answer"] == "جواب"
    assert result["hits"] == []
    assert result["trace"] == [{"tool": "grammar_correction"}]
    assert result["thread_id"] == 7


def test_no_errors_reply_passes_contract_unchanged():
    """رد "لا أخطاء" مختلف الشكل يجب ألا يكسر العقد (hits تبقى [])."""
    result = uc.build_grammar_result("النص صحيح ولا أخطاء فيه", thread_id=3)
    assert result["hits"] == []
    assert "صحيح" in result["answer"]
