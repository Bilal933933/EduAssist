"""حالة استخدام توليد البطاقات — Application orchestration للفيتشر.

تضم ما كان مبعثراً في الـ endpoint: تحقق ← استرجاع هجين ← توليد.
الـ Router يعرف HTTP فقط.
"""
from app.agent import embed_question, generate_flashcards, generate_quiz
from app.knowledge.retrieval_log import log_retrieval
from app.modules.cards.validation import validate_topic
from app.modules.chat.validation import validate_question


class CardsService:
    """GenerateFlashcardsUseCase + GenerateQuizUseCase في خدمة واحدة متماسكة."""

    def generate_flashcards(self, topic: str, question: str | None, client, kb) -> dict:
        import time as _t
        topic = validate_topic(topic)
        if question:
            validate_question(question)
        _s = _t.perf_counter()
        hits = kb.hybrid_search(topic, None, top_k=5, embed_fn=lambda: embed_question(client, topic))
        try:
            _m = (hits[0].get("retrieval_mode", "") if hits else "hybrid")
            log_retrieval(question or topic, hits, scope={"topic": topic}, mode=_m, latency_ms=(_t.perf_counter() - _s) * 1000, route="flashcards")
        except Exception:
            pass
        cards = generate_flashcards(client, hits, topic)
        return {"cards": cards, "topic": topic}

    def generate_quiz(self, topic: str, question: str | None, client, kb) -> dict:
        import time as _t
        topic = validate_topic(topic)
        if question:
            validate_question(question)
        _s = _t.perf_counter()
        hits = kb.hybrid_search(topic, None, top_k=5, embed_fn=lambda: embed_question(client, topic))
        try:
            _m = (hits[0].get("retrieval_mode", "") if hits else "hybrid")
            log_retrieval(question or topic, hits, scope={"topic": topic}, mode=_m, latency_ms=(_t.perf_counter() - _s) * 1000, route="quiz")
        except Exception:
            pass
        quiz = generate_quiz(client, hits, topic)
        return {"quiz": quiz, "topic": topic}
