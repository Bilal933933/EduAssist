import hashlib
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

from unittest.mock import MagicMock

from src.indexing.indexer_service import IndexerService
from app.modules.knowledge_ingestion.application.run_indexing_use_case import (
    run_indexing,
)


def _key(chunk):
    raw = f"{chunk.get('source','')}|{chunk.get('title','')}|{chunk.get('page','')}|{chunk.get('text','')[:200]}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:32]


class FakeVS:
    def __init__(self, keys=None):
        self._keys = set(keys or set())
        self.upserted = []
        self.prune_calls = []

    def sync_metadata(self, chunks):
        return 0

    def existing_doc_keys(self):
        return set(self._keys)

    def _generate_doc_key(self, chunk):
        return _key(chunk)

    def upsert(self, chunk, vector):
        self.upserted.append(chunk)

    def prune_not_in(self, active_keys):
        self.prune_calls.append(set(active_keys))
        return 0

    def count(self):
        return len(self.upserted) + len(self._keys)


def _chunks():
    return [
        {"source": "كتاب", "title": "الفاعل", "subject": "العربية",
         "grade": "grade5", "text": "نص الفاعل"},
        {"source": "كتاب", "title": "المفعول", "subject": "العربية",
         "grade": "grade5", "text": "نص المفعول"},
    ]


def _service(monkeypatch, fake):
    svc = IndexerService(vector_service=fake)
    chunks = _chunks()
    monkeypatch.setattr(svc, "load_sections", lambda: [{"dummy": 1}])
    monkeypatch.setattr(svc, "chunk", lambda sections: list(chunks))
    return svc, chunks


def test_prune_false_never_deletes_and_embeds_hierarchical(monkeypatch):
    """حارس زر المعلم: prune=False ← لا حذف إطلاقاً + تضمين هرمي موحد."""
    chunks = _chunks()
    fake = FakeVS(keys={_key(chunks[0])})  # الأولى مفهرسة، الثانية جديدة
    svc, _ = _service(monkeypatch, fake)
    seen = {}

    def fake_embed(client, texts, batch_size):
        seen["texts"] = list(texts)
        yield [[0.1] * 4]

    result = run_indexing(svc, MagicMock(), prune=False, embed_fn=fake_embed)
    assert fake.prune_calls == []  # الحارس: لا استدعاء إطلاقاً
    assert result["indexed"] == 1 and result["deleted"] == 0
    assert len(fake.upserted) == 1
    assert seen["texts"] == [svc.embedding_text(chunks[1])]  # الصيغة الهرمية لا القديمة
    assert " — " not in seen["texts"][0]  # ليست صيغة reindex.py القديمة


def test_prune_true_deletes_with_active_keys(monkeypatch):
    """حارس CLI: prune=True ← حذف بالمفاتيح النشطة الصحيحة."""
    chunks = _chunks()
    fake = FakeVS(keys={_key(chunks[0]), _key(chunks[1])})
    svc, _ = _service(monkeypatch, fake)

    def fake_embed(client, texts, batch_size):
        if False:
            yield []

    result = run_indexing(svc, MagicMock(), prune=True, embed_fn=fake_embed)
    assert len(fake.prune_calls) == 1
    assert fake.prune_calls[0] == {_key(c) for c in chunks}
    assert result["deleted"] == 0 and result["indexed"] == 0
