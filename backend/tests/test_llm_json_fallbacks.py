"""سقوط مواقع JSON الثمانية بعد التوحيد — سياسة كل موقع محفوظة حرفيًا."""
import pytest

GARBAGE = "عذرًا لا يوجد جيسون هنا"
BROKEN = '{"ranking": [3, 1,'
HITS = [{"title": f"عنوان {i}", "text": f"نص المقطع {i} عن الفاعل", "source": "مرجع"} for i in range(8)]


@pytest.fixture
def garbage_client(monkeypatch):
    monkeypatch.setattr("app.agent.fc_client.call_simple", lambda *a, **k: GARBAGE)


def test_cards_fallbacks(garbage_client):
    from app.agent.cards import generate_flashcards, generate_quiz
    assert generate_flashcards(None, HITS) == []
    assert generate_quiz(None, HITS) == []


def test_cards_valid_shape(monkeypatch):
    from app.agent.cards import generate_flashcards
    monkeypatch.setattr(
        "app.agent.fc_client.call_simple",
        lambda *a, **k: 'مقدمة {"cards": [{"q": "س1", "a": "ج1"}]} ذيل',
    )
    assert generate_flashcards(None, HITS) == [{"q": "س1", "a": "ج1"}]


def test_validator_conservative(garbage_client):
    from app.agent.validator import validate_citations
    valid, corrected, issues = validate_citations(None, "إجابة طويلة" * 50, HITS)
    assert (valid, corrected, issues) == (True, "إجابة طويلة" * 50, [])


def test_classifier_rejects(garbage_client):
    from app.query_analyzer.llm_classifier import _parse_result
    assert _parse_result(GARBAGE) == (None, 0.0)
    assert _parse_result(BROKEN) == (None, 0.0)
    assert _parse_result('{"intent": "hack", "confidence": 0.9}') == (None, 0.0)
    assert _parse_result('{"intent": "explain", "confidence": 0.8}') == ("explain", 0.8)


def test_decomposer_deterministic_expansion(garbage_client):
    from app.agent.decomposer import decompose_question
    qs = decompose_question(None, "أنشئ تدريبات على الفاعل", intent="generate_exercises")
    assert len(qs) > 1
    assert any("الفاعل" in q for q in qs)


def test_critic_keep_all_batch(garbage_client):
    from app.agent.critic import judge_and_filter
    hits = [{"title": "t", "text": "نص عن الفاعل", "source": "s", "branch": "نحو"}]
    verdict, info = judge_and_filter(None, "اشرح الفاعل", hits, kb=None, scope={}, pillars=[])
    assert verdict == hits


def test_ragas_neutral(garbage_client):
    from app.evaluation.ragas import evaluate
    out = evaluate(None, "س؟", "ج" * 50, HITS)
    assert out["faithfulness"] == 5 and out["relevance"] == 5


def test_reranker_passthrough(garbage_client):
    from app.agent.reranker.llm import rerank_llm_prompt
    assert rerank_llm_prompt(None, "س؟", HITS, top_k=3) == HITS[:3]
