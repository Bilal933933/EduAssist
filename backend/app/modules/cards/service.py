"""حالة استخدام توليد البطاقات — Application orchestration للفيتشر.

تضم ما كان مبعثراً في الـ endpoint: تحقق ← استرجاع هجين ← توليد.
الـ Router يعرف HTTP فقط.
"""
from app.agent import embed_question, generate_flashcards, generate_quiz
from app.modules.cards.validation import validate_topic
from app.modules.chat.validation import validate_question


class CardsService:
    """GenerateFlashcardsUseCase + GenerateQuizUseCase في خدمة واحدة متماسكة."""

    def generate_flashcards(self, topic: str, question: str | None, client, kb) -> dict:
        topic = validate_topic(topic)
        if question:
            validate_question(question)
        hits = kb.hybrid_search(topic, None, top_k=5, embed_fn=lambda: embed_question(client, topic))
        cards = generate_flashcards(client, hits, topic)
        return {"cards": cards, "topic": topic}

    def generate_quiz(self, topic: str, question: str | None, client, kb) -> dict:
        topic = validate_topic(topic)
        if question:
            validate_question(question)
        hits = kb.hybrid_search(topic, None, top_k=5, embed_fn=lambda: embed_question(client, topic))
        quiz = generate_quiz(client, hits, topic)
        return {"quiz": quiz, "topic": topic}
