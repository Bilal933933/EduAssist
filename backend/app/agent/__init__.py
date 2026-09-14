"""نقطة الدخول الموحدة للـ Agent — تعيد التصدير من التنفيذ المعتمد.

التنفيذ المعتمد حالياً: app.modules.lesson_knowledge.application.agent
خارطة الطريق: نقل الملفات فيزيائياً إلى هنا، ثم حذف modules/lesson_knowledge.
"""
from app.modules.lesson_knowledge.application.agent.cards import generate_flashcards, generate_quiz
from app.modules.lesson_knowledge.application.agent.chat import ask, build_prompt, embed_question
from app.modules.lesson_knowledge.application.agent.clarifier import extract_scope, needs_clarification
from app.modules.lesson_knowledge.application.agent.critic import judge_and_filter, judge_relevance
from app.modules.lesson_knowledge.application.agent.decomposer import decompose_question
from app.modules.lesson_knowledge.application.agent.fc_client import call_simple, call_with_tools
from app.modules.lesson_knowledge.application.agent.generator import build_teacher_prompt
from app.modules.lesson_knowledge.application.agent.loop import run_agentic_rag, run_agentic_rag_stream
from app.modules.lesson_knowledge.application.agent.prompts import TEACHER_SYSTEM
from app.modules.lesson_knowledge.application.agent.reranker import rerank_llm, rerank_local
from app.modules.lesson_knowledge.application.agent.router import get_chitchat_reply, route
from app.modules.lesson_knowledge.application.agent.sub_agents import run_sub_agents, synthesize_lesson
from app.modules.lesson_knowledge.application.agent.validator import validate_citations

__all__ = [
    "run_agentic_rag", "run_agentic_rag_stream", "decompose_question",
    "validate_citations", "extract_scope", "needs_clarification",
    "judge_relevance", "judge_and_filter", "route", "get_chitchat_reply",
    "call_with_tools", "call_simple", "build_teacher_prompt", "build_prompt",
    "ask", "embed_question", "rerank_local", "rerank_llm",
    "run_sub_agents", "synthesize_lesson", "generate_flashcards",
    "generate_quiz", "TEACHER_SYSTEM",
]
