import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.agent.tools import format_search_observation
from src.agent.fc_client import call_simple
from src.agent.generator import build_teacher_prompt
from src.agent.plugins.clarify import run as clarify_run
from src.agent.plugins.decompose import run as decompose_run
from src.agent.plugins.search import run_loop as search_run
from src.core.logger import Timer

def run(client, kb, question, history=None, max_iterations=4, analysis=None):
    # clarify
    clar = clarify_run(client, kb, question, analysis)
    if clar.get("needs"):
        return f"CLARIFY: {clar['question']}", [], [{"tool": "clarify", "question": clar["question"]}]

    # sub-agents for lesson prep
    if "حضر" in question and "درس" in question:
        try:
            from src.agent.sub_agents import run_sub_agents, synthesize_lesson
            timer = Timer(f"SubAgents: {question[:30]}")
            parts, topic, grade = run_sub_agents(client, kb, question)
            all_hits = []
            for v in parts.values():
                all_hits.extend(v.get("hits", []))
            answer = synthesize_lesson(client, parts, topic, grade)
            trace = [{"tool": f"subAgent:{k}", "hits": len(v.get("hits",[]))} for k,v in parts.items()]
            timer.end(f"sub-agents hits={len(all_hits)}")
            return answer, all_hits[:14], trace
        except Exception as e:
            print(f"[SubAgents fallback: {e}]")

    from src.agent.clarifier import extract_scope
    scope = extract_scope(question)
    history_text = "\n".join(f"{r}: {t}" for r,t in (history or []))

    # decompose
    try:
        sub_queries, hits, trace = decompose_run(client, kb, question, scope)
    except Exception as e:
        sub_queries, hits, trace = [question], [], []

    all_hits = hits[:]
    # search loop
    s_hits, file_contents, s_trace, contents = search_run(client, kb, question, sub_queries, history_text, scope, max_iterations)
    all_hits.extend(s_hits)
    trace.extend(s_trace)

    # rerank
    uniq, seen = [], set()
    for h in all_hits:
        k = h.get("doc_key") or h.get("text","")[:120]
        if k not in seen:
            seen.add(k); uniq.append(h)
    all_hits = uniq
    if len(all_hits) > 6:
        try:
            from src.agent.reranker import rerank_llm
            all_hits = rerank_llm(client, question, all_hits, top_k=10)
            trace.append({"tool": "rerank", "hits": len(all_hits)})
        except:
            all_hits = all_hits[:10]
    else:
        all_hits = all_hits[:10]

    # generate
    if analysis is not None:
        try:
            from src.query_analyzer.composer import compose
            ev_text = format_search_observation(all_hits[:8])
            system, user = compose(analysis, evidence_text=ev_text)
            if history:
                user += f"\n\n[سياق المحادثة]\n" + "\n".join(f"{r}: {t[:200]}" for r,t in history[-4:])
            if file_contents:
                user += "\n\n[ملفات]\n" + "\n".join(f"{k}: {v[:400]}" for k,v in file_contents.items())
        except Exception:
            system, user = build_teacher_prompt(question, all_hits, history, file_contents)
    else:
        system, user = build_teacher_prompt(question, all_hits, history, file_contents)

    answer = call_simple(client, user, system)
    trace.append({"tool": "generate", "hits": len(all_hits)})
    return answer, all_hits, trace
