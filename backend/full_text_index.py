import sys
sys.path.insert(0, '.')
from src.loader import load_all_sources
from src.loader.chunker import chunk_sections
from src.knowledge.vector_service import VectorService
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
        # متجه صفري 768
        vs.upsert(c, [0.0]*768)
        new += 1
print(f'Inserted text-only: {new}, total now {vs.count()}')
