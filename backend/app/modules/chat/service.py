from app.core.errors import AppError
from app.core.logging import get_logger
from app.core.validation import ensure_thread_exists, validate_teacher_id, validate_thread_id
from app.knowledge.retrieval_log import log_retrieval
from app.modules.chat.validation import validate_question
from app.dependencies import get_summary_repo
from app.agent import call_simple, get_chitchat_reply, route, run_agentic_rag, run_agentic_rag_stream
from app.query_analyzer.analyzer import analyze
from app.modules.tutor_orchestrator.application.route_message_use_case import (
    resolve_module,
)
from app.modules.tutor_orchestrator.domain.intent import ModuleIntent
from app.modules.grammar_correction.application.correct_text_use_case import (
    build_grammar_result,
    correct_text,
)
from app.modules.conversation.application.continue_conversation_use_case import (
    build_conversation_result,
    continue_conversation,
    maybe_update_summary,
)


def _direct_answer(question: str, client) -> str:
    """رد فوري للتحيات بلا أي بحث. ثابت أولاً، ثم LLM عند الغموض."""
    fixed = get_chitchat_reply(question)
    if fixed:
        return fixed
    try:
        return call_simple(
            client,
            question,
            "أنت مساعد المدرس الذكي للغة العربية. رد باختصار ولطف بالعربية. إن سُئلت عن هويتك عرّف نفسك كمساعد تحضير دروس العربية.",
        )
    except Exception:
        return "أهلاً بك! كيف أساعدك في دروس اللغة العربية اليوم؟"


def _update_teacher_memory(analysis, question: str, teacher_id: str = "default"):
    """يحدّث ذاكرة المدرس بعد تفاعل ناجح (لا يرفع استثناء للخارج)."""
    try:
        from app.storage.teacher_memory import TeacherMemoryStore

        grade = None
        topic = None
        if analysis is not None:
            scope = getattr(analysis, "scope", None)
            if scope is not None:
                grade = getattr(scope, "grade", None)
                if not isinstance(grade, str):
                    value = getattr(grade, "value", None)
                    grade = value if isinstance(value, str) else None
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
        get_logger("app").debug(f"TeacherMemory update skip: {e}")


_FILLER_QUESTIONS = frozenset([
    "؟", "?", "؟؟", "الخامس", "السادس", "الرابع",
    "الخامس الابتدائي", "السادس", "الأول", "الثاني", "الثالث",
])

# ردود إقرار قصيرة: جواب على سؤال المساعد السابق (نعم/لا/تمام...)
# — تُفهم من سياق الحوار فقط، لا من المصادر.
_SHORT_ACKS = frozenset([
    "لا", "لأ", "نعم", "اجل", "أجل", "تمام", "طيب", "حسنا", "حسناً",
    "اكيد", "أكيد", "ماشي", "موافق", "تماما", "تماماً", "حاضر",
    "كمل", "أكمل", "اكمل", "تابع", "ok",
])


def _is_short_ack(question: str) -> bool:
    """رد قصير (≤12 حرفاً) من قائمة الإقرارات المغلقة بعد تجريد علامات الترقيم."""
    q = (question or "").strip().strip("؟?!.…-ـ ").strip()
    return bool(q) and len(q) <= 12 and q in _SHORT_ACKS


def _build_context(history: list) -> dict:
    """سياق المحلل من كامل السجل — لا من آخر سؤال فقط.

    يمسح رسائل المدرس من الأحدث للأقدم ويجمع: الموضوع (أقرب حامل له)
    + الصف/المرحلة (أقرب حامل لهما) + النية (من أحدث رسالة غير حشو).
    لخيط من رسالة واحدة يطابق السلوك القديم تماماً.
    """
    from app.query_analyzer.analyzer import analyze as _a

    user_msgs = [t for r, t in (history or []) if r == "user"]
    if not user_msgs:
        return {}
    prev_q = next(
        (t for t in reversed(user_msgs) if t.strip() not in _FILLER_QUESTIONS), ""
    )
    if not prev_q:
        prev_q = user_msgs[-1]
    topic = grade = stage = subject = branch = intent = None
    for msg in reversed(user_msgs):
        try:
            a = _a(msg)
        except Exception:
            continue
        if topic is None:
            topic = a.scope.topic or (a.topics[0] if a.topics else None)
            if topic is not None:
                if subject is None and a.scope.subject.value:
                    subject = a.scope.subject.value
                if branch is None and a.scope.branch.value:
                    branch = a.scope.branch.value
        if grade is None and a.scope.grade.value:
            grade = a.scope.grade.value
            stage = a.scope.stage.value
            subject = a.scope.subject.value
            branch = a.scope.branch.value
        if intent is None and msg.strip() == prev_q.strip():
            intent = a.intent
        if topic is not None and grade is not None and intent is not None:
            break
    if intent is None:
        try:
            intent = _a(prev_q).intent
        except Exception:
            intent = None
    if not any([topic, grade, intent]):
        return {}
    return {
        "grade": grade,
        "stage": stage,
        "subject": subject,
        "branch": branch,
        "topic": topic,
        "intent": intent,
        "prev_question": prev_q,
    }


def _resolve(question: str, context: dict):
    """نقطة التوجيه الوحيدة: analyze ← module ← mode.

    تُستدعى من handle() وstream() معاً حتى لا ينحرف المنطق بينهما (DRY).
    """
    analysis = analyze(question, context)
    module = resolve_module(analysis)
    mode = route(analysis)
    return analysis, module, mode


class ChatService:
    """Feature service — analyzer → clarify → retrieval → compose → LLM."""

    async def _run_conversation(
        self, question: str, thread_id, client, store, teacher_id: str = "default",
        skip_memory: bool = False,
    ):
        """النواة المشتركة لمسار المحادثة (عادي + بث): ملخص تراكمي ← سياق
        (حديث + نبرة المدرس قراءة فقط) ← توليد ← تخزين. تعيد (answer, thread_id).

        skip_memory للتحيات (chitchat): الذاكرة لا تنفعها ومصدر هلوسة
        (صف/موضوع من خيوط أخرى يتسرب للتحية).
        """
        summary_repo = get_summary_repo()
        try:
            # التلخيص تحسين ثانوي (تدهور رشيق): فشله لا يوقف الرد الأساسي.
            maybe_update_summary(client, summary_repo, store, thread_id)
        except Exception:
            pass
        state = summary_repo.get(thread_id)
        history = store.recent_history(thread_id)
        memory_block = ""
        if not skip_memory:
            try:
                from app.storage.teacher_memory import TeacherMemoryStore

                memory_block = TeacherMemoryStore().get_prompt_block(teacher_id) or ""
            except Exception:
                memory_block = ""
        answer = continue_conversation(
            client, question, history, state["summary"], memory_block
        )
        store.add_message(thread_id, "user", question)
        store.add_message(thread_id, "assistant", answer, sources=[])
        return answer, thread_id

    async def _run_grammar_correction(self, question: str, thread_id, client, store):
        """النواة المشتركة لمسار التصحيح (عادي + بث): إيجاد/إنشاء thread ←
        تصحيح LLM بلا RAG ← تخزين. تعيد (answer, thread_id)."""
        # TODO: تمرير التصحيحات إلى teacher_mistakes (مؤجل — خارج نطاق المرحلة 2)
        if thread_id is None:
            thread_id = store.create_thread(title=question[:50])["id"]
        store.add_message(thread_id, "user", question)
        answer = correct_text(client, question)
        store.add_message(thread_id, "assistant", answer, sources=[])
        return answer, thread_id

    async def handle(
        self, question: str, thread_id: int | None, client, kb, store, teacher_id: str = "default"
    ):
        question = validate_question(question)
        teacher_id = validate_teacher_id(teacher_id)
        thread_id = validate_thread_id(thread_id)
        if thread_id is not None:
            ensure_thread_exists(store, thread_id)
        context = {}
        if thread_id is not None:
            context = _build_context(store.recent_history(thread_id))
        # المرحلة 1: module محسوب وموثق فقط — كل الوحدات تستخدم
        # السلوك الحالي نفسه (صفر تغيير سلوكي).
        # TODO(المرحلة 2): توجيه GRAMMAR/CONVERSATION لوحداتهما.
        analysis, module, mode = _resolve(question, context)
        _ = module
        # رد قصير داخل خيط قائم (لا/نعم/تمام): جواب على سؤال المساعد السابق
        # — يُجاب من سياق الحوار لا من المصادر.
        if (
            thread_id is not None
            and module is ModuleIntent.LESSON_KNOWLEDGE
            and _is_short_ack(question)
        ):
            module = ModuleIntent.CONVERSATION_PRACTICE
        # المحادثة داخل thread قائم فقط — الجديدة تسقط للمسار المباشر الحالي.
        # (resolve_module نقية: نية ← وحدة؛ شرط السياق هنا في طبقة التنسيق)
        if module is ModuleIntent.CONVERSATION_PRACTICE and thread_id is not None:
            answer, thread_id = await self._run_conversation(
                question, thread_id, client, store, teacher_id,
                skip_memory=(analysis.intent == "chitchat" or _is_short_ack(question)),
            )
            return build_conversation_result(answer, thread_id)
        if mode == "direct":
            if thread_id is None:
                thread_id = store.create_thread(title=question[:50])["id"]
            answer = _direct_answer(question, client)
            store.add_message(thread_id, "user", question)
            store.add_message(thread_id, "assistant", answer, sources=[])
            return {"answer": answer, "hits": [], "trace": [{"tool": "direct"}], "thread_id": thread_id}
        if module is ModuleIntent.GRAMMAR_CORRECTION:
            answer, thread_id = await self._run_grammar_correction(
                question, thread_id, client, store
            )
            return build_grammar_result(answer, thread_id)
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
        import time as _t
        _start = _t.perf_counter()
        answer, hits, trace = run_agentic_rag(
            client,
            kb,
            question,
            history,
            max_iterations=3,
            analysis=analysis,
            teacher_id=teacher_id,
            light=(mode == "light"),
        )
        try:
            _scope = getattr(getattr(analysis, "scope", None), "__dict__", None) or {}
            if not isinstance(_scope, dict):
                _scope = {"scope": str(getattr(analysis, "scope", ""))[:80]}
            _mode = (hits[0].get("retrieval_mode", "") if hits else ("light" if mode == "light" else "deep"))
            log_retrieval(question, hits, scope=_scope, mode=_mode, latency_ms=(_t.perf_counter() - _start) * 1000, route="chat", thread_id=thread_id)
        except Exception:
            pass
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
        question = validate_question(question)
        teacher_id = validate_teacher_id(teacher_id)
        thread_id = validate_thread_id(thread_id)
        if thread_id is not None:
            ensure_thread_exists(store, thread_id)
        is_new = thread_id is None
        history = store.recent_history(thread_id) if thread_id is not None else []
        context = _build_context(history) if thread_id is not None else {}
        # المرحلة 1: انظر التعليق في handle() — نفس السلوك الحالي لكل الوحدات.
        analysis, module, mode = _resolve(question, context)
        _ = module
        # رد قصير داخل خيط قائم (لا/نعم/تمام): جواب على سؤال المساعد السابق
        # — يُجاب من سياق الحوار لا من المصادر.
        if (
            thread_id is not None
            and module is ModuleIntent.LESSON_KNOWLEDGE
            and _is_short_ack(question)
        ):
            module = ModuleIntent.CONVERSATION_PRACTICE
        if module is ModuleIntent.CONVERSATION_PRACTICE and thread_id is not None:
            answer, thread_id = await self._run_conversation(
                question, thread_id, client, store, teacher_id,
                skip_memory=(analysis.intent == "chitchat" or _is_short_ack(question)),
            )
            result = build_conversation_result(answer, thread_id)

            async def conversation_gen():
                yield {"type": "answer_chunk", "text": result["answer"]}
                yield {
                    "type": "done",
                    "hits": result["hits"],
                    "trace": result["trace"],
                    "full": result["answer"],
                }
            # المحفوظة=True: المسار المخزَّن تكفّل بحفظ رسالة المساعد، فلا يعيد الراوتر حفظها.
            return conversation_gen(), result["thread_id"], True
        if mode == "direct":
            if is_new:
                thread_id = store.create_thread(title=question[:50])["id"]
            store.add_message(thread_id, "user", question)
            answer = _direct_answer(question, client)
            store.add_message(thread_id, "assistant", answer, sources=[])

            async def direct_gen():
                yield {"type": "answer_chunk", "text": answer}
                yield {"type": "done", "hits": [], "trace": [{"tool": "direct"}], "full": answer}
            # المحفوظة=True: answer حُفظت أعلاه، فلا يكررها الراوتر.
            return direct_gen(), thread_id, True
        if module is ModuleIntent.GRAMMAR_CORRECTION:
            answer, thread_id = await self._run_grammar_correction(
                question, thread_id, client, store
            )
            result = build_grammar_result(answer, thread_id)

            async def grammar_gen():
                yield {"type": "answer_chunk", "text": result["answer"]}
                yield {
                    "type": "done",
                    "hits": result["hits"],
                    "trace": result["trace"],
                    "full": result["answer"],
                }
            # المحفوظة=True: التصحيح حُفظ داخل _run_grammar_correction.
            return grammar_gen(), result["thread_id"], True
        if is_new and analysis.needs_clarification:
            async def clarify_gen():
                import json
                yield f"data: {json.dumps({'type': 'clarification', 'question': analysis.clarification_question, 'options': []}, ensure_ascii=False)}\n\n"
            return clarify_gen(), None, False
        if is_new:
            thread_id = store.create_thread(title=question[:50])["id"]
        store.add_message(thread_id, "user", question)
        _update_teacher_memory(analysis, question, teacher_id=teacher_id)
        # المحفوظة=False: رسالة المساعد تُبنى من البث، فيحفظها الراوتر بعد اكتماله.
        import time as _t2
        _start2 = _t2.perf_counter()
        _base_gen = run_agentic_rag_stream(
            client, kb, question, history, analysis=analysis, teacher_id=teacher_id,
            light=(mode == "light"),
        )

        async def _logging_gen():
            _hits: list = []
            async for event in _base_gen:
                if isinstance(event, dict) and event.get("type") == "done":
                    _hits = event.get("hits", []) or []
                yield event
            try:
                _scope2 = getattr(getattr(analysis, "scope", None), "__dict__", None) or {}
                if not isinstance(_scope2, dict):
                    _scope2 = {"scope": str(getattr(analysis, "scope", ""))[:80]}
                _mode2 = (_hits[0].get("retrieval_mode", "") if _hits else ("light" if mode == "light" else "deep"))
                log_retrieval(question, _hits, scope=_scope2, mode=_mode2, latency_ms=(_t2.perf_counter() - _start2) * 1000, route="chat_stream", thread_id=thread_id)
            except Exception:
                pass

        return (_logging_gen(), thread_id, False)
