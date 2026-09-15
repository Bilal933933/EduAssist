import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.agent.tools import format_search_observation
from app.agent.loop.helpers import _ev_tag, _grade_topic_from_analysis, _load_memory_block
from app.agent.generator import build_teacher_prompt


def deduplicate_hits(all_hits: list) -> list:
    uniq = []
    seen = set()
    for h in all_hits or []:
        if not isinstance(h, dict):
            continue
        k = h.get("doc_key") or h.get("text", "")[:120]
        if k not in seen:
            seen.add(k)
            uniq.append(h)
    return uniq


def critic_filter(client, question, hits, kb, scope):
    """بوابة الصلة: نقد الأدلة + بحث موجه — يعيد (hits, info|None)."""
    try:
        from app.agent.critic import judge_and_filter
        from app.agent.decomposer import get_pillars
        filtered, info = judge_and_filter(
            client, question, hits, kb, scope, max_retries=1, pillars=get_pillars(question)
        )
        return filtered, info
    except Exception as e:
        print(f"[Critic skip: {e}]")
        return hits, None


def rerank_top(client, question, hits, top_k: int = 10) -> list:
    if len(hits or []) > 6:
        try:
            from app.agent.reranker import rerank_llm
            return rerank_llm(client, question, hits, top_k=top_k)
        except Exception:
            return (hits or [])[:top_k]
    return (hits or [])[:top_k]


def compose_final_prompt(question, hits, history, file_contents, analysis, scope, teacher_id="default"):
    """Prompt Composer الجديد إن وجد analysis — وإلا build_teacher_prompt مع ذاكرة."""
    if analysis is not None:
        try:
            from app.query_analyzer.composer import compose
            ev_text = format_search_observation(hits[:8])
            system, user = compose(
                analysis,
                evidence_text=ev_text + "\n\n" + "\n".join(
                    f"{_ev_tag(h)} {h.get('text')[:500]}" for h in hits[:8]
                ),
            )
            if history:
                user += "\n\n[سياق المحادثة]\n" + "\n".join(f"{r}: {t[:200]}" for r, t in history[-4:])
            if file_contents:
                user += "\n\n[ملفات]\n" + "\n".join(f"{k}: {v[:400]}" for k, v in file_contents.items())
            return system, user
        except Exception as e:
            print(f"[Composer fallback: {e}]")
    g, t = _grade_topic_from_analysis(analysis)
    memory_block = _load_memory_block(teacher_id, current_grade=g, current_topic=t)
    return build_teacher_prompt(
        question, hits, history, file_contents,
        memory_block=memory_block, scope=scope, analysis=analysis,
    )


def validate_answer(client, answer, hits):
    """تحقق الاستشهاد للأجوبة الطويلة — يعيد (answer, info|None)."""
    if not (len(hits or []) > 0 and len(answer or "") > 200):
        return answer, None
    try:
        from app.agent.validator import validate_citations
        valid, corrected, issues = validate_citations(client, answer, hits)
        info = {"tool": "validate", "valid": valid, "issues": issues[:2] if issues else []}
        if not valid and corrected and len(corrected) > 100:
            return corrected, info
        return answer, info
    except Exception as e:
        print(f"[Validate skip: {e}]")
        return answer, None
