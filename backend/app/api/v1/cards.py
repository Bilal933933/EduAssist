from fastapi import APIRouter, Depends
from google import genai

from app.agent import embed_question, generate_flashcards, generate_quiz
from app.core.errors import AppError
from app.core.response import ok
from app.core.validation import validate_question, validate_topic
from app.dependencies import get_gemini_client, get_kb
from app.schemas.cards import CardsRequest

router = APIRouter(prefix="/api", tags=["cards"])


@router.post("/flashcards")
async def flashcards(req: CardsRequest, client: genai.Client = Depends(get_gemini_client), kb=Depends(get_kb)):
    try:
        topic = validate_topic(req.topic)
        if req.question:
            validate_question(req.question)
        hits = kb.hybrid_search(topic, None, top_k=5, embed_fn=lambda: embed_question(client, topic))
        cards = generate_flashcards(client, hits, topic)
        return ok({"cards": cards, "topic": topic})
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.post("/quiz")
async def quiz(req: CardsRequest, client: genai.Client = Depends(get_gemini_client), kb=Depends(get_kb)):
    try:
        topic = validate_topic(req.topic)
        if req.question:
            validate_question(req.question)
        hits = kb.hybrid_search(topic, None, top_k=5, embed_fn=lambda: embed_question(client, topic))
        quiz = generate_quiz(client, hits, topic)
        return ok({"quiz": quiz, "topic": topic})
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")
