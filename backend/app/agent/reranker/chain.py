"""منسق طبقات الترتيب: BGE ← FlashRank ← heuristic ← LLM (اختياري).

RERANK_HEURISTIC_FIRST=1 يقدّم heuristic على FlashRank (مفيد عربياً بلا BGE).
RERANK_LLM_LAST=1 يعيد طبقة LLM كخيار أخير (تستهلك حصة).
"""
import os

from app.agent.reranker.bge import rerank_bge
from app.agent.reranker.flashrank_backend import rerank_local
from app.agent.reranker.heuristic import prefer_first, rerank_heuristic
from app.agent.reranker.llm import rerank_llm_prompt
from app.agent.reranker.shared import small_pool


def rerank_llm(client, question: str, hits: list, top_k: int = 10) -> list:
    sp = small_pool(hits, top_k)
    if sp is not None:
        return sp

    if prefer_first():
        print(f"[Rerank] heuristic-first: {len(hits)} → {min(top_k, len(hits))}")
        return rerank_heuristic(question, hits, top_k)

    bge = rerank_bge(question, hits, top_k)
    if bge is not None:
        print(f"[Rerank] BGE: {len(hits)} → {len(bge)}")
        return bge

    local = rerank_local(question, hits, top_k)
    if local is not None:
        print(f"[Rerank] محلي: {len(hits)} → {len(local)}")
        return local

    if os.getenv("RERANK_LLM_LAST", "0") == "1":
        llm_ranked = rerank_llm_prompt(client, question, hits, top_k)
        if llm_ranked is not None:
            return llm_ranked

    print(f"[Rerank] heuristic: {len(hits)} → {min(top_k, len(hits))}")
    return rerank_heuristic(question, hits, top_k)
