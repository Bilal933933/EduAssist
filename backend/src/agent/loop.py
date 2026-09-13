import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from google.genai import types

from src.core.logger import get_logger, Timer
from src.agent.tools import execute_tool, format_search_observation
from src.agent.prompts import AGENT_SYSTEM_FC
from src.agent.fc_client import call_with_tools, call_simple, MODEL_NAME, types as fc_types
from src.agent.generator import build_teacher_prompt
from src.agent.clarifier import extract_scope

logger = get_logger("agent")


def _load_memory_block(teacher_id: str = "default", current_grade: str | None = None, current_topic: str | None = None) -> str:
    """يحمّل كتلة ذاكرة المدرس مربوطة بالصف/الموضوع الحالي."""
    try:
        from src.storage.teacher_memory import TeacherMemoryStore
        return TeacherMemoryStore().get_prompt_block(
            teacher_id, current_grade=current_grade, current_topic=current_topic
        )
    except Exception as e:
        print(f"[Memory skip: {e}]")
        return ""


def _ev_tag(h: dict) -> str:
    """ترويسة دليل مشروطة: بلا 'صNone' عند غياب الصفحة."""
    src = h.get("source") or "مصدر"
    page = h.get("page")
    return f"[{src} ص{page}]" if page else f"[{src}]"


def _grade_topic_from_analysis(analysis) -> tuple:
    grade = topic = None
    if analysis is None:
        return grade, topic
    scope = getattr(analysis, "scope", None)
    if scope is not None:
        grade = getattr(getattr(scope, "grade", None), "value", None) or getattr(scope, "grade", None)
        topic = getattr(scope, "topic", None)
    if not topic and getattr(analysis, "topics", None):
        topic = analysis.topics[0] if analysis.topics else None
    if isinstance(grade, str) and grade in ("unknown", "غير محدد", ""):
        grade = None
    return (str(grade) if grade else None), (str(topic) if topic else None)



def run_agentic_rag(client, kb, question, history=None, max_iterations=4, analysis=None, teacher_id="default"):
    """حلقة مع طبقة استيضاح قبل التفكيك. analysis يأتي من QueryAnalyzer (intent/scope/source_policy)."""
    # 0. استيضاح عبر Analyzer الجديد إن وجد، وإلا fallback للقديم
    if analysis is not None and getattr(analysis, "needs_clarification", False):
        return f"CLARIFY: {analysis.clarification_question}", [], [{"tool": "clarify", "question": analysis.clarification_question, "options": []}]
    try:
        quick_hits = kb.vector_service.lexical_search(question, top_k=5)
        from src.agent.clarifier import needs_clarification
        clar = needs_clarification(question, quick_hits)
        if clar:
            return f"CLARIFY: {clar['question']}", [], [{"tool": "clarify", "question": clar["question"], "options": clar["options"]}]
    except Exception as e:
        print(f"[Clarify skip: {e}]")

    # إذا كان طلب تحضير درس، شغّل 4 وكلاء
    if "حضر" in question and "درس" in question:
        try:
            from src.agent.sub_agents import run_sub_agents, synthesize_lesson
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
        from src.agent.decomposer import decompose_question
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
    uniq=[]
    seen=set()
    for h in all_hits:
        k=h.get("doc_key") or h.get("text","")[:120]
        if k not in seen:
            seen.add(k); uniq.append(h)
    all_hits=uniq
    # بوابة الصلة: نقد الأدلة + بحث موجه للمحاور الناقصة (مرة واحدة) قبل الـ rerank
    try:
        from src.agent.critic import judge_and_filter
        from src.agent.decomposer import get_pillars
        all_hits, critic_info = judge_and_filter(client, question, all_hits, kb, question_scope, max_retries=1, pillars=get_pillars(question))
        trace.append({"tool": "critic", **critic_info})
    except Exception as e:
        print(f"[Critic skip: {e}]")
    if len(all_hits) > 6:
        try:
            from src.agent.reranker import rerank_llm
            all_hits = rerank_llm(client, question, all_hits, top_k=10)
            trace.append({"tool": "rerank", "hits": len(all_hits)})
        except: all_hits=all_hits[:10]
    else:
        all_hits=all_hits[:10]

    print(f"[Agent-FC] نهائي: {len(all_hits)} قطع + {len(file_contents)} ملفات → توليد (بعد Rerank)")
    # استخدام Prompt Composer الجديد إن وجد analysis
    if analysis is not None:
        try:
            from src.query_analyzer.composer import compose
            ev_text = format_search_observation(all_hits[:8])
            system, user = compose(analysis, evidence_text=ev_text + "\n\n" + "\n".join(f"{_ev_tag(h)} {h.get('text')[:500]}" for h in all_hits[:8]))
            # أضف السياق والملفات للـ user
            if history:
                user += f"\n\n[سياق المحادثة]\n" + "\n".join(f"{r}: {t[:200]}" for r,t in history[-4:])
            if file_contents:
                user += "\n\n[ملفات]\n" + "\n".join(f"{k}: {v[:400]}" for k,v in file_contents.items())
        except Exception as e:
            print(f"[Composer fallback: {e}]")
            g, t = _grade_topic_from_analysis(analysis)
            memory_block = _load_memory_block(teacher_id, current_grade=g, current_topic=t)
            system, user = build_teacher_prompt(question, all_hits, history, file_contents, memory_block=memory_block)
    else:
        g, t = _grade_topic_from_analysis(analysis)
        memory_block = _load_memory_block(teacher_id, current_grade=g, current_topic=t)
        system, user = build_teacher_prompt(question, all_hits, history, file_contents, memory_block=memory_block)
    answer = call_simple(client, user, system)
    trace.append({"tool": "generate", "hits": len(all_hits)})

    # 2.1 تحقق الاستشهاد (اختياري - لا يبطئ إذا كان الجواب قصير)
    if len(all_hits) > 0 and len(answer) > 200:
        try:
            from src.agent.validator import validate_citations
            valid, corrected, issues = validate_citations(client, answer, all_hits)
            trace.append({"tool": "validate", "valid": valid, "issues": issues[:2] if issues else []})
            if not valid and corrected and len(corrected) > 100:
                answer = corrected
        except Exception as e:
            print(f"[Validate skip: {e}]")

    # Ragas تقييم (لا يؤثر على الإجابة)
    try:
        from src.evaluation.ragas import evaluate
        scores = evaluate(client, question, answer, all_hits)
        trace.append({"tool": "ragas", "faith": scores["faithfulness"], "relev": scores["relevance"]})
        logger.info(f"Ragas faith={scores['faithfulness']:.2f} relev={scores['relevance']:.2f}")
    except: pass

    timer.end(f"hits={len(all_hits)} trace={len(trace)}")
    logger.info(f"trace: {trace}")
    return answer, all_hits, trace


async def run_agentic_rag_stream(client, kb, question, history=None, max_iterations=4, analysis=None, teacher_id="default"):
    """نسخة Streaming مع استيضاح."""
    question_scope = extract_scope(question)
    if analysis is not None and getattr(analysis, "needs_clarification", False):
        yield {"type": "clarification", "question": analysis.clarification_question, "options": []}
        return
    import asyncio
    # 0. استيضاح
    try:
        quick_hits = kb.vector_service.lexical_search(question, top_k=5)
        from src.agent.clarifier import needs_clarification
        clar = needs_clarification(question, quick_hits)
        if clar:
            yield {"type": "clarification", "question": clar["question"], "options": clar["options"]}
            return
    except Exception as e:
        print(f"[Clarify stream skip: {e}]")

    all_hits=[]
    file_contents={}
    trace=[]

    # تفكيك (موجّه بنية الـ Analyzer إن وجدت)
    _intent_s = getattr(analysis, "intent", None) if analysis is not None else None
    try:
        from src.agent.decomposer import decompose_question
        sub_queries = decompose_question(client, question, max_queries=5, intent=_intent_s)
        yield {"type": "status", "message": f"يفكك السؤال إلى {len(sub_queries)} استعلامات..."}
        await asyncio.sleep(0)
        if len(sub_queries) > 1:
            for sq in sub_queries[:5]:
                yield {"type": "status", "message": f"يبحث عن: {sq}"}
                hits = execute_tool("searchChunks", {"query": sq, "top_k": 20}, kb, client, inherited_scope=question_scope)
                if isinstance(hits, list):
                    all_hits.extend(hits)
                    trace.append({"tool": "searchChunks", "args": {"query": sq}, "decomposed": True})
                await asyncio.sleep(0)
    except Exception as e:
        sub_queries = [question]

    history_text="\n".join(f"{r}: {t}" for r,t in (history or []))
    contents = [types.Content(role="user", parts=[types.Part(text=f"سؤال المدرس: {question}\nالاستعلامات: {sub_queries}\nالسياق: {history_text[:800]}")])]

    for iteration in range(max_iterations):
        yield {"type": "status", "message": f"يفكر (دورة {iteration+1})..."}
        try:
            resp = call_with_tools(client, contents, AGENT_SYSTEM_FC)
        except Exception as e:
            break
        cand = resp.candidates[0] if resp.candidates else None
        if not cand or not cand.content or not cand.content.parts:
            break
        part = cand.content.parts[0]
        if hasattr(part, "function_call") and part.function_call and part.function_call.name:
            name = part.function_call.name
            args = dict(part.function_call.args) if part.function_call.args else {}
            yield {"type": "status", "message": f"يستدعي {name}: {args.get('query', args.get('path',''))[:40]}"}
            result = execute_tool(name, args, kb, client, inherited_scope=question_scope)
            if isinstance(result, list):
                all_hits.extend(result)
                obs_text = format_search_observation(result, max_hits=8, max_chars=600)
            else:
                file_contents[args.get("path","")] = result
                obs_text = f"ملف ({len(result)} حرف)"
            contents.append(cand.content)
            contents.append(types.Content(role="user", parts=[types.Part(function_response=types.FunctionResponse(name=name, response={"result": obs_text[:2000]}))]))
            trace.append({"tool": name, "args": args})
            if len(all_hits) >= 40:
                break
            continue
        else:
            break

    uniq=[]
    seen=set()
    for h in all_hits:
        k=h.get("doc_key") or h.get("text","")[:120]
        if k not in seen:
            seen.add(k); uniq.append(h)
    all_hits=uniq
    # بوابة الصلة (stream): نقد + بحث موجه مرة واحدة قبل الـ rerank
    try:
        yield {"type": "status", "message": "يراجع صلة الأدلة..."}
        from src.agent.critic import judge_and_filter
        from src.agent.decomposer import get_pillars
        all_hits, critic_info = judge_and_filter(client, question, all_hits, kb, question_scope, max_retries=1, pillars=get_pillars(question))
        trace.append({"tool": "critic", **critic_info})
    except Exception as e:
        print(f"[Critic stream skip: {e}]")
    if len(all_hits) > 6:
        try:
            from src.agent.reranker import rerank_llm
            yield {"type": "status", "message": "يعيد ترتيب النتائج..."}
            all_hits = rerank_llm(client, question, all_hits, top_k=10)
        except: all_hits=all_hits[:10]
    else:
        all_hits=all_hits[:10]

    yield {"type": "status", "message": "يولد الإجابة..."}
    if analysis is not None:
        try:
            from src.query_analyzer.composer import compose
            ev_text = format_search_observation(all_hits[:8], max_hits=8, max_chars=600)
            system, user = compose(analysis, evidence_text=ev_text + "\n\n" + "\n".join(f"{_ev_tag(h)} {h.get('text')[:400]}" for h in all_hits[:8]))
            if history:
                user += "\n\n[سياق]\n" + "\n".join(f"{r}: {t[:150]}" for r,t in history[-4:])
            if file_contents:
                user += "\n\n[ملفات]\n" + "\n".join(f"{k}: {v[:300]}" for k,v in file_contents.items())
        except Exception as e:
            print(f"[Composer stream fallback: {e}]")
            g, t = _grade_topic_from_analysis(analysis)
            memory_block = _load_memory_block(teacher_id, current_grade=g, current_topic=t)
            system, user = build_teacher_prompt(question, all_hits, history, file_contents, memory_block=memory_block)
    else:
        g, t = _grade_topic_from_analysis(analysis)
        memory_block = _load_memory_block(teacher_id, current_grade=g, current_topic=t)
        system, user = build_teacher_prompt(question, all_hits, history, file_contents, memory_block=memory_block)

    # streaming للتوليد النهائي
    full = ""
    try:
        from google.genai import types as gen_types
        for chunk in client.models.generate_content_stream(model=MODEL_NAME, contents=user, config=gen_types.GenerateContentConfig(system_instruction=system)):
            if chunk.text:
                full += chunk.text
                yield {"type": "answer_chunk", "text": chunk.text}
                await asyncio.sleep(0)
    except:
        # fallback غير متدفق
        full = call_simple(client, user, system)
        for i in range(0, len(full), 80):
            yield {"type": "answer_chunk", "text": full[i:i+80]}
            await asyncio.sleep(0.02)

    # تحقق
    if len(all_hits) > 0 and len(full) > 200:
        try:
            from src.agent.validator import validate_citations
            valid, corrected, issues = validate_citations(client, full, all_hits)
            if not valid and corrected and len(corrected) > 100:
                full = corrected
                yield {"type": "answer_correct", "text": corrected}
        except: pass

    yield {"type": "done", "hits": all_hits, "trace": trace, "full": full}
