"""طبقة LLM الأصلية — محفوظة كخيار أخير خلف RERANK_LLM_LAST=1 (تستهلك حصة)."""
import json
import re

from app.agent.reranker.shared import small_pool

RERANK_PROMPT = """رتب هذه المقتطفات حسب صلة مباشرة بسؤال المدرس.

سؤال المدرس: "{question}"

المقتطفات:
{chunks}

أجب JSON فقط:
{{"ranking": [3, 1, 5, 2, ...]}}
حيث الأرقام هي فهارس المقتطفات من الأكثر صلة للأقل. أعد الكل مرتباً.
"""


def _rows(hits: list) -> list:
    rows = []
    for i, h in enumerate(hits):
        meta = " | ".join(
            x for x in [
                f"المصدر: {h.get('source') or 'غير محدد'}",
                f"الصف: {h.get('grade') or 'عام'}",
                f"المادة: {h.get('subject') or 'غير محددة'}",
                f"الوحدة: {h.get('unit') or '-'}",
                f"الدرس: {h.get('lesson') or h.get('title') or '-'}",
                f"الصفحة: {h.get('page') or '-'}",
            ]
            if x
        )
        rows.append(f"{i+1}. [{meta}]\n{(h.get('text') or '')[:700]}")
    return rows


def rerank_llm_prompt(client, question: str, hits: list, top_k: int = 10) -> list | None:
    sp = small_pool(hits, top_k)
    if sp is not None:
        return sp
    prompt = RERANK_PROMPT.format(question=question, chunks="\n\n".join(_rows(hits)))
    try:
        from app.agent.fc_client import call_simple
        raw = call_simple(client, prompt, "أنت مرتب. أجب JSON فقط.")
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return hits[:top_k]
        ranking = json.loads(m.group()).get("ranking", list(range(1, len(hits) + 1)))
        ranked, seen = [], set()
        for idx in ranking:
            if 1 <= idx <= len(hits) and idx not in seen:
                ranked.append(hits[idx - 1])
                seen.add(idx)
        for idx, h in enumerate(hits, start=1):
            if idx not in seen:
                ranked.append(h)
        print(f"[Rerank] {len(hits)} → {len(ranked[:top_k])} مرتب")
        return ranked[:top_k]
    except Exception as e:
        print(f"[Rerank skip: {e}]")
        return hits[:top_k]
