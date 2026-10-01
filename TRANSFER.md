# TRANSFER.md — تجميد v1 (384 محلي)

## قرار التجميد
- التخزين والاستعلام: `e5-small` محلي (`LOCAL_EMBEDDING_PATH`) ببعد `384` حصرًا.
- القاعدة: `knowledge_chunks.embedding vector(384)`، الامتداد `vector 0.8.6` مفعّل، 12704 صفوف بلا فراغ (2026-10-01).
- النسخة الاحتياطية قبل التغيير: `backups/ai_grammar_pre_vector768.backup`.

## قيود v1 (ملزمة)
- يُمنع تشغيل `cli.py` (تضمين Gemini ‏768) ضد هذه القاعدة — يكسر الأبعاد. الردم عبر `scripts/embed_local.py` فقط.
- `embed_question` في `chat.py` يتجاهل `client` عمدًا ويستخدم المحلي مع بادئة `query:` (مقابل `passage:` في التخزين).
- `search.py` يبحث `numpy` داخل بايثون؛ لا `‎<=>‎` ولا `HNSW` في v1.

## بنود v2
- عمود `embedding_model` لكل صف + تسجيل النموذج الفعلي لكل دفعة.
- توحيد Gemini ‏(`gemini-embedding-2` ‏768) تخزينًا واستعلامًا مع إعادة تضمين كاملة.
- `‎<=>‎` داخل القاعدة + فهرس `HNSW` بعد توحيد البعد.
- السياق من القاعدة بدل `readFile`، وتسامح `NULL` في `_where_clause`.
