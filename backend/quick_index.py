import sys
sys.path.insert(0, '.')
import os
from dotenv import load_dotenv
load_dotenv()
from google import genai
from app.modules.knowledge_ingestion.infrastructure.loaders import load_all_sources
from app.modules.knowledge_ingestion.infrastructure.loaders.chunker import chunk_sections
from app.knowledge.embeddings import embed_batches, BATCH_SIZE
from app.knowledge.vector_service import VectorService
vs=VectorService()
client=genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
sections=load_all_sources()
chunks=chunk_sections(sections)
print(f'chunks {len(chunks)} from {len(sections)} sections')
chunks=chunks[:50]
texts=[f"{c.get('source','')} - {c['title']}: {c['text']}" for c in chunks]
idx=0
for batch in embed_batches(client, texts, BATCH_SIZE):
    for c, v in zip(chunks[idx:idx+len(batch)], batch):
        vs.upsert(c, v)
    idx+=len(batch)
    print(f'done {idx}/50')
print('saved', vs.count())
