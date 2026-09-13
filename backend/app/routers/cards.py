from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from google import genai
from app.dependencies import get_gemini_client, get_kb
from src.agent.cards import generate_flashcards, generate_quiz
from src.agent.chat import embed_question

router = APIRouter(prefix="/api", tags=["cards"])

class CardsRequest(BaseModel):
    topic: str
    question: str = ""

@router.post("/flashcards")
async def flashcards(req: CardsRequest, client: genai.Client = Depends(get_gemini_client), kb=Depends(get_kb)):
    try:
        qvec = embed_question(client, req.topic)
        hits = kb.hybrid_search(req.topic, qvec, top_k=5)
        cards = generate_flashcards(client, hits, req.topic)
        return {"cards": cards, "topic": req.topic}
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/quiz")
async def quiz(req: CardsRequest, client: genai.Client = Depends(get_gemini_client), kb=Depends(get_kb)):
    try:
        qvec = embed_question(client, req.topic)
        hits = kb.hybrid_search(req.topic, qvec, top_k=5)
        quiz = generate_quiz(client, hits, req.topic)
        return {"quiz": quiz, "topic": req.topic}
    except Exception as e: raise HTTPException(500, str(e))
