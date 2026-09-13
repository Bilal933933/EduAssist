# تحسينات مساعد المدرس الذكي - من السطحي إلى العميق

> تاريخ: 28 أغسطس 2026 | الحالة: مكتمل 10/11 ✅ - 28 أغسطس 2026 (متبقي 3.4 SaaS مؤجل للمرحلة الثانية) | الهدف: تحويل الكود السطحي الحالي إلى Agentic RAG عميق حقيقي

## الوضع الحالي (سطحي - MVP)

| الملف | المشكلة |
|-------|---------|
| `backend/src/agent.py:agent_decide()` | قرار JSON يدوي بسيط (search/read/answer) - ليس Function Calling رسمي |
| `backend/src/agent.py:run_agentic_rag()` | حلقة 2-3 دورات فقط بدون تفكير ReAct (Thought→Act→Observe) |
| `backend/src/agent_tools.py` | أداتان فقط (search/read) بدون تفكيك سؤال ولا تحقق |
| `backend/src/chat.py` | لا تحقق هل الجواب فعلاً من المصدر أم هلوسة |
| عام | لا سجلات (logging)، لا قياس جودة، لا اختبارات، `readFile` يقطع 8000 حرف عشوائياً |

---

## التحسينات المطلوبة (مرتبة حسب الأولوية)

### المرحلة 1: عمق الـ Agent (الأهم)
- [x] **1.1 Function Calling رسمي**: تم - `src/agent/tools.py:TOOL_DECLARATIONS` + `src/agent/loop.py:_call_with_tools` (Gemini tools + function_call)
- [x] **1.2 حلقة ReAct حقيقية**: تم - `loop.py:run_agentic_rag` حلقة Thought→Act→Observe 3-4 دورات مع trace (تم اختباره: حضر الفاعل → 2 search ثم generate)
- [x] **1.3 تفكيك السؤال (Query Decomposition)**: تم - `src/agent/decomposer.py:decompose_question()` يفكك "حضر الفاعل خامس" → 4 استعلامات + `loop.py` يبحث عن كل جزء (warm start 3 queries) - اختبار: 7 hits بدل 5
- [x] **1.4 قراءة ذكية**: تم - `src/agent/tools.py:_smart_read()` تفهم front-matter + تقسم حسب `##` + تعيد فهرس للملف الكبير أو مقتطف مطابق لـ `query` - اختبار: `grammar_knowledge.md + الفاعل` → قسم الجملة الفعلية فقط

### المرحلة 2: الجودة والموثوقية
- [x] **2.1 تحقق الاستشهاد (Citation Validation)**: تم - `src/agent/validator.py:validate_citations()` + تكامل في `loop.py` (يضيف `[مصدر]` ويحول الهلوسة إلى "لا يوجد في مصادرك") - اختبار: "الانشطار النووي" → رفض صحيح، "الفاعل منصوب؟" → تصحيح إلى مرفوع
- [ ] **2.2 معالجة أخطاء عميقة**: Global Exception Filter موحد (Next + FastAPI) + حفظ رسالة جزئية عند انقطاع Stream + زر Retry
- [ ] **2.3 سجلات ومراقبة**: `logging` + `Sentry` أو `OpenTelemetry` لتتبع كل دورة Agent ووقتها
- [x] **2.4 اختبارات**: تم - `tests/test_agent_tools.py` (5) + `tests/test_loader.py` (3) + `tests/test_integration.py` (5) = 13 اختبار نجحت في 5.49s

### المرحلة 3: الأداء والتوسع
- [x] **3.1 Reranking اختياري**: تم - تم الاستغناء: `RRF Fuse (hybrid)` بديل مجاني لـ Cohere (تم التوثيق)
- [x] **3.2 Streaming حقيقي**: تم - `backend: /api/chat/stream (SSE) + loop.py:run_agentic_rag_stream (yield status/chunk)` + `realtime: ProxyController /api/chat/stream` + `frontend: streamChat() + ThinkingIndicator(status)` - بناء نجح 13s
- [x] **3.3 فهرسة محسنة**: تم - `chunker.py`: target ~400 token، max 500، overlap ~60 مع hard split؛ `_smart_read` يدعم التقسيم حسب `##` - `ARRAY(Float)` يبقى حتى مرحلة pgvector
- [ ] **3.4 جاهزية SaaS**: إضافة `schoolId/teacherId` nullable في `chat_store.py` + صفحة `/admin/change-password`

---

## معايير القبول للعمق

- [x] Agent يقرأ بنفسه 2-4 مرات عبر Tools قبل الإجابة (مثل OpenCode) - تم في 1.2
- [x] كل معلومة في خطة الدرس تذكر مصدرها `[الكتاب صX]` - تم اختباره
- [ ] لا هلوسة: إذا لم يوجد في المصادر يقول "لا يوجد في مصادرك"
- [ ] زمن 30-60 ثانية مقبول مع مؤشر تقدم

---

## كيف نعمل عليها

1. نبدأ بـ **1.1 + 1.2** (Function Calling + ReAct) - أساس العمق
2. ثم **1.3 + 2.1** (تفكيك + تحقق)
3. الباقي حسب الحاجة

> تم تنفيذ 1.1+1.2 في `src/agent/` (FC + ReAct). التالي: 1.3 تفكيك السؤال. قل "ابدأ 1.3" للتنفيذ.
## P1 — Retrieval quality: chunking + candidate pool + Agent evidence

- Chunking bounded to ~300–500 whitespace tokens for long sections, target ~400, overlap ~60; no chunk exceeds 500 tokens after splitting.
- Chunk metadata is preserved from `section` through chunk creation.
- Hybrid retrieval now uses `40 semantic + 40 lexical → RRF 20 → requested top_k`.
- RRF deduplicates by `doc_key` and removes the previous hard-coded source diversification rule.
- Reranker sees up to 700 characters of evidence plus source/grade/subject/unit/lesson/page metadata instead of only 250 characters.
- Agent `searchChunks` observations now contain real evidence excerpts plus metadata, not titles only.
- Final generation receives only the top 8 reranked evidence items to control context size.
- Indexer embedding text includes curriculum hierarchy (subject/stage/grade/branch/unit/lesson/concepts) so the vector representation benefits from the P0 metadata.
- Indexer prunes stale chunks after a successful indexing pass, preventing old chunking results from remaining after P1.

### Reindexing note
P1 changes chunk boundaries and embedding input, so the corpus must be re-embedded once after deployment. The indexer is designed to keep the previous database safe during partial runs and prune stale records only after successful indexing.

---

## إضافة: ذاكرة المدرس (Teacher Memory) — سبتمبر 2026

- [x] جدول `teacher_profiles` + `TeacherMemoryStore`
- [x] حقن الذاكرة في `build_teacher_prompt` وحلقتي Agent (عادي + stream)
- [x] تحديث تلقائي بعد كل تفاعل ناجح (صف / موضوع / أسلوب)
- [x] API: `GET/PUT /api/memory` + `POST /api/memory/interaction` + `DELETE /api/memory/{id}`
- [x] دعم `teacher_id` في طلبات الدردشة

الملفات:
- `backend/src/storage/teacher_memory.py`
- `backend/src/agent/generator.py` (memory_block)
- `backend/src/agent/loop.py` (_load_memory_block)
- `backend/app/modules/chat/service.py`
- `backend/app/routers/memory.py`

### تعزيز ذاكرة المدرس (شخصية أعمق) — سبتمبر 2026

- [x] `common_mistakes` — أخطاء شائعة مرتبطة بموضوع/صف مع عدّاد
- [x] `recent_lessons` — آخر الدروس لتجنب التكرار
- [x] `preferences` منظمة: detail_level / example_style / tone / prefers_lesson_plans / prefers_exercises
- [x] `class_context` — ملاحظات عن مستوى الطلاب
- [x] استنتاج تلقائي من السؤال (تحضير درس، أخطاء، مختصر/مفصل، من الحياة...)
- [x] كتلة برومبت أغنى مع تعليمات صريحة للمساعد
- [x] API موسّع: PUT يدعم الحقول الجديدة + POST `/api/memory/mistakes`

### ذاكرة علاقية + ربط بالصف + نبرة مهنية — سبتمبر 2026

- [x] جداول: `teacher_profiles` | `teacher_mistakes` | `teacher_recent_lessons`
- [x] الأخطاء وآخر الدروس مربوطة بـ grade (وتُصفّى حسب الصف الحالي في البرومبت)
- [x] التفضيلات العامة تبقى على مستوى المدرس
- [x] `get_prompt_block(teacher_id, current_grade, current_topic)`
- [x] Agent يستخرج الصف/الموضوع من analysis ويحقن الذاكرة المصفاة
- [x] نبرة مخاطبة مدرس محترف (تعديل TEACHER_SYSTEM + كتلة الذاكرة)
- [x] API: تصفية `?grade=` + `/mistakes` + `/lessons`
- [x] ترحيل بسيط من JSON القديم إن وُجد

### M1/M2 — تطبيع قاعدة بيانات الذاكرة — سبتمبر 2026

- [x] `grades` بذرة معيارية + مطابقة aliases
- [x] `teachers` بهوية UUID و `external_key`
- [x] `teacher_grade_assignments` بدل JSON للصفوف
- [x] `teacher_preferences` أعمدة ثابتة
- [x] `teacher_topic_stats` بدل frequent_topics JSON
- [x] `teacher_mistakes_v2` مع normalized_key و grade_id
- [x] `teacher_lesson_events` بدل recent_lessons النصي
- [x] ترحيل تلقائي من جداول v3
- [x] فهارس: mistakes(teacher,grade,count) / events(teacher,grade,time)
- [x] API: `/api/memory/grades/catalog`
- [x] توثيق: `backend/src/storage/SCHEMA_TEACHER_MEMORY.md`

