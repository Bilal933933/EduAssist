"""[legacy_v2 مجمّد — ممنوع التشغيل] فهرسة نصية بمتجه صفري مؤقت.
v1 يستخدم chunk_and_store.py (نصي) + embed_local.py (384 passage:) حصرًا.
يُرفع فورًا ما لم يُفعّل ALLOW_LEGACY_GEMINI_EMBED=1 (لترحيل v2 فقط)."""
import os as _os

if _os.getenv("ALLOW_LEGACY_GEMINI_EMBED", "0") != "1":
    raise RuntimeError(
        "LEGACY_GEMINI_EMBED_FROZEN: full_text_index.py مجمّد — استخدم "
        "scripts/chunk_and_store.py ثم scripts/embed_local.py (384)"
    )
import sys
sys.path.insert(0, '.')
from app.modules.knowledge_ingestion.infrastructure.loaders import load_all_sources
from app.modules.knowledge_ingestion.infrastructure.loaders.chunker import chunk_sections
from app.knowledge.vector_service import VectorService
import numpy as np

vs = VectorService()
sections = load_all_sources()
chunks = chunk_sections(sections)
print(f'Total chunks: {len(chunks)}')
existing = vs.existing_doc_keys()
print(f'Existing: {len(existing)}')

# أدخل كل النصوص بمتجه صفري مؤقت ليٌعمل البحث النصي فوراً
new = 0
for c in chunks:
    key = vs._generate_doc_key(c)
    if key not in existing:
        # متجه صفري 384 (كان 768 قبل التجميد — الخلط يكسر الأعمدة)
        vs.upsert(c, [0.0]*384)
        new += 1
print(f'Inserted text-only: {new}, total now {vs.count()}')
