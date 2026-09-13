# مساعد المدرس الذكي للغة العربية - ملف السياق (AGENTS.md)

هذا الملف هو المرجع الوحيد لجميع الوكلاء (Agents) العاملين على المشروع. أي كود يُكتب يجب أن يلتزم به حرفياً.

## 1. هوية المشروع

- **الاسم:** مساعد المدرس الذكي - لغة عربية
- **العميل:** مدرس واحد (حساب خاص)، قابل للتحول لـ SaaS بإضافة `schoolId/teacherId` لاحقاً
- **الهدف:** تحضير الدروس وخطط الشرح وسير الحصة عبر **Agentic RAG عميق** من مصادره الخاصة فقط
- **اللغة:** عربية 100% RTL
- **المنصة:** Web PWA (يعمل بدون تثبيت، قابل للتثبيت)
- **المبدأ:** الجودة > السرعة (مسموح 30-60 ثانية)

## 2. المعمارية المثبتة

```
Next.js (PWA)  -->  FastAPI (RAG Worker)  -->  Postgres + pgvector
     |                     |
     +-- realtime (NestJS) للـ Socket/Streaming (موجود في docker-compose)
```

- **القرار:** `Next.js + FastAPI` (خدمتين) + `realtime` Gateway موجود مسبقاً - لا نضيف Laravel
- **النشر:** `docker-compose.yml` (postgres:16 + ai-chat:8000 + realtime:3001) - المنفذ الوحيد المكشوف 3001

## 3. المكدس التقني المثبت

| الطبقة | الأداة |
|--------|--------|
| واجهة | Next.js 16 + React 19 + TypeScript + Tailwind v4 + shadcn/ui + next-themes + sonner (RTL) |
| حالة | TanStack Query (سيرفر) + Zustand (واجهة) - ممنوع fetch في useEffect |
| باك اند AI | FastAPI + google-genai + sqlalchemy + pgvector |
| Gateway | NestJS + Socket.IO (realtime/) |
| قاعدة بيانات | PostgreSQL 16 + pgvector |
| LLM | `gemini-3.5-flash-lite` (سريع، حدود مجانية واسعة) مع fallback `3.5-flash -> 3.6-flash` |
| Embeddings | `gemini-embedding-2` (768 بُعد) مع fallback `gemini-embedding-001` (مجاني) |
| Vector Search | Hybrid (دلالي + معجمي) + RRF Fuse (بديل Reranker) - لا Cohere |

## 4. حقائق حرجة (يُمنع كسرها)

- **Embedding Consistency:** `embed_question` يجب أن يستخدم نفس النموذج والأبعاد المخزنة. خلط `embedding-001` و `embedding-2` يكسر البحث (similarity < 0.7)
- **BATCH_SIZE = 1:** `gemini-embedding-2` يعيد متجه واحد فقط حتى لو أرسلت عدة نصوص. ممنوع batching
- **Rate Limit 429:** احترم `retryDelay` من Google. `chat.py` يبدل النموذج، `embedder.py` يبدل نموذج التضمين
- **Resume Indexing:** `indexer.py` يحفظ التقدم في `store/` - عند انقطاعه أعد تشغيله وسيكمل من حيث توقف
- **Encoding:** كل سكربت بايثون يجب أن يحتوي `sys.stdout.reconfigure(encoding='utf-8')`
- **Reindex:** يدوي عبر زر في الواجهة `POST /api/reindex` - لا Cron
- **Auth:** كلمة مرور قابلة للتغيير من `/admin` (hash في DB) - لا كلمة ثابتة في ENV فقط

## 5. هيكلة المصادر (M2 + pedagogy)

```
content/
├── textbook/primary/grade5/...        # المنهج (Markdown + front-matter)
├── references/general/...             # مراجع نحو عامة
└── pedagogy/                          # ★ الطبقة التربوية (source_type=pedagogy) - منفصلة تماماً
    ├── methods/primary|prep|general/          # طرائق تدريس اللغة العربية
    ├── classroom/primary|prep|general/        # إدارة الصف، التهيئة، التقويم
    ├── differentiation/primary|prep|general/  # مراعاة الفروق، معالجة الأخطاء
    └── assessment/primary|prep|general/       # بناء أسئلة، تقويم تكويني
```

- كل مصدر Markdown مقسم حسب `##` + `## صفحة N`
- التقسيم: ~700 token + overlap 100 عبر `src/chunker.py` (و `semantic_chunker.py` ~400 للطويل)
- كل مجلد كتاب يملك `metadata.json` أو `front-matter` يحدد `source_type, stage, grade, subject, branch, book_id`
- `source_type` مصرح: `textbook | teacher_guide | reference | pedagogy | general` — الفهرسة تحفظه في `knowledge_chunks.source_type`
- `pedagogy` لا يختلط مع `textbook/reference` في الاسترجاع الافتراضي؛ يُستدعى بفلتر `source_type=pedagogy + stage/grade` لطبقة إعادة الصياغة التربوية
- بعد تغيير النموذج/الأبعاد: احذف `store/chunks.json` و `store/vectors.npy` ثم `python src/indexer.py`

## 6. المتطلبات الوظيفية

| المعرف | الميزة | الوصف |
|--------|--------|-------|
| FR-01 | التحضير المباشر | "حضر لي درس الفاعل - الخامس" -> خطة شرح + سير حصة من مصادره |
| FR-02 | النقاش التفاعلي | "ما أفضل أسلوب لشرح الفاعل؟" -> عدة أساليب تعليمية |
| FR-03 | المصادر | عربية فقط، هيكلة content المذكورة |
| FR-04 | Agentic RAG | Agent يقرأ بنفسه عبر Tools (searchChunks + readFile) 2-4 مرات |
| FR-05 | Reranking | RRF Fuse يعيد أفضل 5 مقاطع فقط للـ LLM |
| FR-06 | السجل والبحث | حفظ كل محادثة بسياقها + بحث لاحق |
| FR-07 | الواجهة | عربية 100% PWA |

## 7. نموذج البيانات

```
User(id) - Thread(id, userId, title) - Message(id, threadId, role, content, sources) - SourceChunk(id, path, content, embedding vector(768))
 grades(id, code, label_ar, stage) - teachers(id UUID, external_key, display_name) - teacher_grade_assignments - teacher_preferences - teacher_topic_stats - teacher_mistakes_v2 - teacher_lesson_events
```
- الذاكرة M1/M2 مطبقة في `backend/src/storage/teacher_memory.py:142-235` (سبعة جداول + `external_key='default'` + ترحيل v3 + فهارس للبرومبت)
- جاهز لـ SaaS: إضافة `schoolId/teacherId` nullable لاحقاً (M3: ربط `chat_threads/lessons` بـ `teachers.id + grade_id`)
- بحث السجل: `pg_trgm` + `tsvector`

## 8. تدفق Agentic RAG (الجديد)

```
سؤال المدرس -> FastAPI /agent/run
  -> Loop 1: searchChunks("الفاعل خامس") -> RRF top5 -> readFile(path)
  -> Loop 2: searchChunks(مكمل) -> readFile
  -> Final: build_prompt(history + hits) -> Gemini -> answer + حفظ
```

## 9. أوامر التطوير

```bash
python src/indexer.py          # فهرسة (مستأنفة، 30-60 دقيقة)
python src/main.py             # محادثة CLI
cd backend && python main.py   # FastAPI :8000
cd realtime && npm run build && npm start  # Gateway :3001
cd frontend && npm run dev     # Next.js
docker-compose up --build      # كل الخدمات
```

## 10. ما تغير عن السابق

- كان: مساعد نحو للطلاب (RAG بسيط 3 hits)
- أصبح: مساعد مدرس (Agentic RAG 2-4 أدوات + تحضير دروس + سير حصة)
- المصادر: من `data/grammar_knowledge.md` إلى `content/textbook + references`
- الواجهة: من CLI إلى PWA عربية كاملة

<!-- lean-ctx -->
## lean-ctx

lean-ctx is active — the MCP tools replace native equivalents.
Full rules: LEAN-CTX.md (open on demand — do not auto-load).
<!-- /lean-ctx -->
