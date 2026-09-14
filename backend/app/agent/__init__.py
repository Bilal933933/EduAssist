"""التنفيذ الفعلي للـ Agent — Modular Monolith.

app/agent هو المالك الوحيد لمنطق الوكيل (loop/tools/reranker).
app/modules/lesson_knowledge أصبح طبقة توافقية مؤقتة تُعاد التصدير من هنا
وستُحذف في النقلة التالية.
"""
from app.agent.cards import generate_flashcards, generate_quiz
from app.agent.chat import ask, build_prompt, embed_question
from app.agent.clarifier import extract_scope, needs_clarification
from app.agent.critic import judge_and_filter, judge_relevance
from app.agent.decomposer import decompose_question
from app.agent.fc_client import call_simple, call_with_tools
from app.agent.generator import build_teacher_prompt
from app.agent.loop import run_agentic_rag, run_agentic_rag_stream
from app.agent.prompts import TEACHER_SYSTEM
from app.agent.reranker import rerank_llm, rerank_local
from app.agent.router import get_chitchat_reply, route
from app.agent.sub_agents import run_sub_agents, synthesize_lesson
from app.agent.validator import validate_citations

__all__ = [
    "run_agentic_rag", "run_agentic_rag_stream", "decompose_question",
    "validate_citations", "extract_scope", "needs_clarification",
    "judge_relevance", "judge_and_filter", "route", "get_chitchat_reply",
    "call_with_tools", "call_simple", "build_teacher_prompt", "build_prompt",
    "ask", "embed_question", "rerank_local", "rerank_llm",
    "run_sub_agents", "synthesize_lesson", "generate_flashcards",
    "generate_quiz", "TEACHER_SYSTEM",
]
