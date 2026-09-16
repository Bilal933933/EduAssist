import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from google.genai import types

from app.core.logging import Timer
from app.agent.tools import execute_tool, format_search_observation
from app.agent.prompts import AGENT_SYSTEM_FC
from app.agent.fc_client import call_with_tools, call_simple
from app.agent.clarifier import extract_scope
from app.agent.loop.helpers import QUOTA_FALLBACK, logger
from app.agent.loop.pedagogy import _is_pedagogy_query, _fetch_pedagogy_hits, _merge_pedagogy
from app.agent.loop.light import _build_light_prompt, _light_search
from app.agent.loop.pipeline import (
    deduplicate_hits, critic_filter, rerank_top, compose_final_prompt, validate_answer,
)


def run_agentic_rag(client, kb, question, history=None, max_iterations=4, analysis=None, teacher_id="default", light=False):
    """حلقة مع طبقة استيضاح قبل التفكيك. analysis يأتي من QueryAnalyzer (intent/scope/source_policy)."""
    # 0. استيضاح عبر Analyzer الجديد فقط — بلا بحث معجمي استباقي (كان يسأل عن الصف حتى للتحيات).
    if analysis is not None and getattr(analysis, "needs_clarification", False):
        return f"CLARIFY: {analysis.clarification_question}", [], [{"tool": "clarify", "question": analysis.clarification_question, "options": []}]
    if analysis is None:
        try:
            quick_hits = kb.vector_service.lexical_search(question, top_k=5)
            from app.agent.clarifier import needs_clarification
            clar = needs_clarification(question, quick_hits)
            if clar:
                return f"CLARIFY: {clar['question']}", [], [{"tool": "clarify", "question": clar["question"], "options": clar["options"]}]
        except Exception as e:
            print(f"[Clarify skip: {e}]")

    # مسار خفيف: بحث واحد + توليد واحد (للإعراب والشرح والأسئلة المفردة).
    if light:
        from app.agent.loop.light import enrich_light_query

        question_scope = extract_scope(question)
        timer = Timer(f"Light: {question[:30]}")
        hits = _light_search(kb, client, question, question_scope, history=history, analysis=analysis)
        enriched = enrich_light_query(question, history, analysis)
        trace = [{"tool": "searchChunks", "args": {"query": enriched}, "light": True, "hits": len(hits)}]
        # Tier2 تربوي منفصل لأسئلة الأسلوب فقط — [] بأمان قبل إضافة الكتب
        _ped = _fetch_pedagogy_hits(kb, client, enriched, question_scope, analysis=analysis) if _is_pedagogy_query(question, analysis) else []
        if _ped:
            hits = _merge_pedagogy(hits, _ped, ped_first=True, limit=13)
            trace.append({"tool": "searchChunks:pedagogy_tier2", "hits": len(_ped)})
        system, user = _build_light_prompt(question, hits, history, analysis=analysis)
        try:
            answer = call_simple(client, user, system)
        except Exception as e:
            print(f"[Light generate fallback: {e}]")
            answer = QUOTA_FALLBACK
            trace.append({"tool": "generate_fallback", "error": str(e)[:120]})
        else:
            trace.append({"tool": "generate", "hits": len(hits)})
        timer.end(f"light hits={len(hits)}")
        return answer, hits[:8], trace

    # بوابة تحضير الدرس: intent مصنف أولاً، ثم fallback نصي عند غياب التحليل.
    _intent_prepare = getattr(analysis, "intent", None) if analysis is not None else None
    _is_prepare = (_intent_prepare == "prepare_lesson") if _intent_prepare else ("حضر" in question and "درس" in question)
    if _is_prepare:
        try:
            from app.agent.sub_agents import run_sub_agents, synthesize_lesson
            timer = Timer(f"SubAgents: {question[:30]}")
            parts, topic, grade = run_sub_agents(client, kb, question)
            # اجمع hits كل الوكلاء
            all_hits = []
            for v in parts.values():
                all_hits.extend(v.get("hits", []))
            answer = synthesize_lesson(client, parts, topic, grade)
            trace = [{"tool": f"subAgent:{k}", "hits": len(v.get("hits",[]))} for k,v in parts.items()]
            timer.end(f"sub-agents hits={len(all_hits)}")
            return answer, all_hits[:14], trace
        except Exception as e:
            print(f"[SubAgents fallback: {e}]")

    question_scope = extract_scope(question)
    timer = Timer(f"Agent: {question[:30]}")
    all_hits=[]
    file_contents={}
    trace=[]
    history_text="\n".join(f"{r}: {t}" for r,t in (history or []) )

    # 1.3 تفكيك السؤال أولاً (موجّه بنية الـ Analyzer إن وجدت)
    _intent = getattr(analysis, "intent", None) if analysis is not None else None
    try:
        from app.agent.decomposer import decompose_question
        sub_queries = decompose_question(client, question, max_queries=5, intent=_intent)
        # إذا فُكك إلى أكثر من 1، ابحث عن كل جزء فوراً قبل الحلقة (warm start) - نرسل الجميع
        if len(sub_queries) > 1:
            for sq in sub_queries[:5]:
                hits = execute_tool("searchChunks", {"query": sq, "top_k": 20}, kb, client, inherited_scope=question_scope)
                if isinstance(hits, list):
                    all_hits.extend(hits)
                    trace.append({"tool": "searchChunks", "args": {"query": sq}, "decomposed": True})
                    print(f"[Decompose] بحث '{sq}' → {len(hits)}")
    except Exception as e:
        print(f"[Decompose skip: {e}]")
        sub_queries = [question]

    # contents للحلقة: نحتفظ بالسياق
    contents = [types.Content(role="user", parts=[types.Part(text=f"سؤال المدرس: {question}\nالاستعلامات الفرعية: {sub_queries}\nالسياق: {history_text[:800]}")])]

    print(f"\n[Agent-FC] بدء: {question[:60]} (تفكيك: {len(sub_queries)} استعلام)")

    for iteration in range(max_iterations):
        try:
            resp = call_with_tools(client, contents, AGENT_SYSTEM_FC)
        except Exception as e:
            print(f"[Agent-FC] فشل FC → {e}")
            break

        cand = resp.candidates[0] if resp.candidates else None
        if not cand or not cand.content or not cand.content.parts:
            break

        part = cand.content.parts[0]

        # هل قرر استدعاء أداة؟
        if hasattr(part, "function_call") and part.function_call and part.function_call.name:
            fc = part.function_call
            name = fc.name
            args = dict(fc.args) if fc.args else {}
            print(f"[Agent-FC دورة {iteration+1}] → {name} {args}")
            trace.append({"tool": name, "args": args})
            result = execute_tool(name, args, kb, client, inherited_scope=question_scope)

            # سجل الـ observation
            if isinstance(result, list):
                all_hits.extend(result)
                obs_text = format_search_observation(result, max_hits=8, max_chars=600)
            else:
                file_contents[args.get("path","")] = result
                obs_text = f"محتوى الملف ({len(result)} حرف): {result[:400]}"

            # أضف للسياق: function_call + function_response
            contents.append(cand.content)
            contents.append(types.Content(role="user", parts=[types.Part(
                function_response=types.FunctionResponse(name=name, response={"result": obs_text[:2000]})
            )]))

            if len(all_hits) >= 40:
                print("[Agent-FC] candidate pool وصل 40 قطعة → ننتقل للـrerank")
                break
            continue
        else:
            text = getattr(part, "text", "") or ""
            if text.strip():
                print(f"[Agent-FC دورة {iteration+1}] نص بدون أداة → نولد الإجابة")
                break
            break

    # Reranking: candidate pool المجمّع → أفضل 10
    all_hits = deduplicate_hits(all_hits)
    # بوابة الصلة: نقد الأدلة + بحث موجه للمحاور الناقصة (مرة واحدة) قبل الـ rerank
    all_hits, critic_info = critic_filter(client, question, all_hits, kb, question_scope)
    if critic_info:
        trace.append({"tool": "critic", **critic_info})
    ranked = rerank_top(client, question, all_hits, top_k=10)
    if len(all_hits) > 6:
        trace.append({"tool": "rerank", "hits": len(ranked)})
    all_hits = ranked

    # Tier2 تربوي منفصل بعد الـ rerank — يتصدر عند سؤال الأسلوب، [] بأمان قبل إضافة الكتب
    try:
        if _is_pedagogy_query(question, analysis):
            _ped = _fetch_pedagogy_hits(kb, client, question, question_scope)
            if _ped:
                all_hits = _merge_pedagogy(all_hits, _ped, ped_first=True, limit=14)
                trace.append({"tool": "searchChunks:pedagogy_tier2", "hits": len(_ped)})
    except Exception as e:
        print(f"[Pedagogy merge skip: {e}]")

    print(f"[Agent-FC] نهائي: {len(all_hits)} قطع + {len(file_contents)} ملفات → توليد (بعد Rerank)")
    system, user = compose_final_prompt(question, all_hits, history, file_contents, analysis, question_scope, teacher_id)
    try:
        answer = call_simple(client, user, system)
    except Exception as e:
        print(f"[Deep generate fallback: {e}]")
        answer = QUOTA_FALLBACK
        trace.append({"tool": "generate_fallback", "error": str(e)[:120]})
        timer.end(f"hits={len(all_hits)} fallback")
        logger.info(f"trace: {trace}")
        return answer, all_hits, trace
    trace.append({"tool": "generate", "hits": len(all_hits)})

    # 2.1 تحقق الاستشهاد (اختياري - لا يبطئ إذا كان الجواب قصير)
    answer, validate_info = validate_answer(client, answer, all_hits)
    if validate_info:
        trace.append(validate_info)

    # Ragas تقييم (لا يؤثر على الإجابة)
    try:
        from app.evaluation.ragas import evaluate
        scores = evaluate(client, question, answer, all_hits)
        trace.append({"tool": "ragas", "faith": scores["faithfulness"], "relev": scores["relevance"]})
        logger.info(f"Ragas faith={scores['faithfulness']:.2f} relev={scores['relevance']:.2f}")
    except: pass

    timer.end(f"hits={len(all_hits)} trace={len(trace)}")
    logger.info(f"trace: {trace}")
    return answer, all_hits, trace
