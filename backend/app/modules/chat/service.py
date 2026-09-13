from fastapi import HTTPException
from src.agent.loop import run_agentic_rag, run_agentic_rag_stream
from src.query_analyzer.analyzer import analyze


def _update_teacher_memory(analysis, question: str, teacher_id: str = "default"):
    """يحدّث ذاكرة المدرس بعد تفاعل ناجح (لا يرفع استثناء للخارج)."""
    try:
        from src.storage.teacher_memory import TeacherMemoryStore

        grade = None
        topic = None
        if analysis is not None:
            scope = getattr(analysis, "scope", None)
            if scope is not None:
                grade = getattr(getattr(scope, "grade", None), "value", None) or getattr(
                    scope, "grade", None
                )
                topic = getattr(scope, "topic", None)
            if not topic and getattr(analysis, "topics", None):
                topic = analysis.topics[0] if analysis.topics else None
            if isinstance(grade, str) and grade in ("unknown", "غير محدد", ""):
                grade = None

        q = question or ""
        is_lesson = any(
            k in q for k in ["حضر", "حضّر", "تحضير", "خطة درس", "سير حصة", "درس عن"]
        )

        TeacherMemoryStore().update_from_interaction(
            teacher_id,
            grade=str(grade) if grade else None,
            topic=str(topic) if topic else None,
            question=question,
            is_lesson_prep=is_lesson,
        )
    except Exception as e:
        print(f"[TeacherMemory update skip: {e}]")


class ChatService:
    """Feature service — analyzer → clarify → retrieval → compose → LLM."""

    async def handle(
        self, question: str, thread_id: int | None, client, kb, store, teacher_id: str = "default"
    ):
        if thread_id is not None and not store.thread_exists(thread_id):
            raise HTTPException(status_code=404, detail="المحادثة غير موجودة.")
        context = {}
        if thread_id is not None:
            hist = store.recent_history(thread_id)
            if hist:
                last_q = ""
                for r, t in reversed(hist):
                    if r == "user" and t.strip() not in [
                        "؟", "?", "؟؟", "الخامس", "السادس", "الرابع",
                        "الخامس الابتدائي", "السادس", "الأول", "الثاني", "الثالث",
                    ]:
                        last_q = t
                        break
                if not last_q:
                    last_q = next((t for r, t in reversed(hist) if r == "user"), "")
                if last_q:
                    from src.query_analyzer.analyzer import analyze as _a
                    ctx_analysis = _a(last_q)
                    context = {
                        "grade": ctx_analysis.scope.grade.value,
                        "stage": ctx_analysis.scope.stage.value,
                        "subject": ctx_analysis.scope.subject.value,
                        "branch": ctx_analysis.scope.branch.value,
                        "topic": ctx_analysis.scope.topic
                        or (ctx_analysis.topics[0] if ctx_analysis.topics else None),
                        "intent": ctx_analysis.intent,
                        "prev_question": last_q,
                    }
        analysis = analyze(question, context)
        if thread_id is None and analysis.needs_clarification:
            return {
                "clarification": {
                    "question": analysis.clarification_question,
                    "options": [],
                },
                "thread_id": None,
            }
        if thread_id is None:
            thread_id = store.create_thread(title=question[:50])["id"]
        history = store.recent_history(thread_id)
        answer, hits, trace = run_agentic_rag(
            client,
            kb,
            question,
            history,
            max_iterations=3,
            analysis=analysis,
            teacher_id=teacher_id,
        )
        if isinstance(answer, str) and answer.startswith("CLARIFY:"):
            return {
                "clarification": {"question": answer.replace("CLARIFY:", "").strip()},
                "thread_id": thread_id,
                "hits": hits,
                "trace": trace,
            }
        store.add_message(thread_id, "user", question)
        store.add_message(thread_id, "assistant", answer, sources=hits)
        _update_teacher_memory(analysis, question, teacher_id=teacher_id)
        return {"answer": answer, "hits": hits, "trace": trace, "thread_id": thread_id}

    async def stream(
        self, question: str, thread_id: int | None, client, kb, store, teacher_id: str = "default"
    ):
        if thread_id is not None and not store.thread_exists(thread_id):
            raise HTTPException(status_code=404, detail="المحادثة غير موجودة.")
        is_new = thread_id is None
        history = store.recent_history(thread_id) if thread_id is not None else []
        context = {}
        if thread_id is not None and history:
            last_q = ""
            for r, t in reversed(history):
                if r == "user" and t.strip() not in [
                    "؟", "?", "؟؟", "الخامس", "السادس", "الرابع",
                    "الخامس الابتدائي", "السادس", "الأول", "الثاني", "الثالث",
                ]:
                    last_q = t
                    break
            if not last_q:
                last_q = next((t for r, t in reversed(history) if r == "user"), "")
            if last_q:
                from src.query_analyzer.analyzer import analyze as _a
                ctx_a = _a(last_q)
                context = {
                    "grade": ctx_a.scope.grade.value,
                    "stage": ctx_a.scope.stage.value,
                    "subject": ctx_a.scope.subject.value,
                    "branch": ctx_a.scope.branch.value,
                    "topic": ctx_a.scope.topic or (ctx_a.topics[0] if ctx_a.topics else None),
                    "intent": ctx_a.intent,
                    "prev_question": last_q,
                }
        analysis = analyze(question, context)
        if is_new and analysis.needs_clarification:
            async def clarify_gen():
                import json
                yield f"data: {json.dumps({'type': 'clarification', 'question': analysis.clarification_question, 'options': []}, ensure_ascii=False)}\n\n"
            return clarify_gen(), None
        if is_new:
            thread_id = store.create_thread(title=question[:50])["id"]
        store.add_message(thread_id, "user", question)
        _update_teacher_memory(analysis, question, teacher_id=teacher_id)
        return (
            run_agentic_rag_stream(
                client, kb, question, history, analysis=analysis, teacher_id=teacher_id
            ),
            thread_id,
        )
