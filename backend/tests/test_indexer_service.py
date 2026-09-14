import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

from unittest.mock import patch

with patch("src.knowledge.vector_service.VectorService.__init__", lambda self, db_url=None: None):
    import src.indexer as legacy

from src.indexing.indexer_service import IndexerService


class FakeVS:
    def __init__(self, count=0, keys=None, pruned=0):
        self._count = count
        self._keys = set(keys or set())
        self._pruned = pruned
        self.prune_arg = None

    def count(self):
        return self._count

    def existing_doc_keys(self):
        return set(self._keys)

    def prune_not_in(self, active_keys):
        self.prune_arg = set(active_keys)
        return self._pruned


def _sample_chunks():
    return [
        {
            "subject": "اللغة العربية", "stage": "primary", "grade": "grade5",
            "branch": "نحو", "unit": "الجملة الاسمية", "lesson": "الفاعل",
            "concepts": ["فاعل", "مرفوع"], "title": "الفاعل",
            "source": "كتاب الخامس", "text": "الفاعل اسم مرفوع يدل على من قام بالفعل.",
        },
        {"title": "بلا هرمية", "source": "مرجع", "text": "نص بسيط", "concepts": "مفهوم مفرد"},
        {"title": "", "source": "", "text": "نص بلا عنوان", "concepts": None},
        {"title": "فراغات", "source": "  ", "subject": "  ", "text": "x", "concepts": []},
        {"text": ""},
    ]


def test_embedding_text_parity_with_legacy():
    """تكافؤ سلوكي: نفس المدخلات ← نفس النص المضمَّن حرفياً."""
    svc = IndexerService(vector_service=FakeVS())
    for chunk in _sample_chunks():
        assert svc.embedding_text(chunk) == legacy._embedding_text(chunk)


def test_load_progress_parity_with_legacy(monkeypatch):
    """تكافؤ الاستئناف: (count, keys) بنفس الدلالة."""
    fake = FakeVS(count=7, keys={"a", "b"})
    monkeypatch.setattr(legacy, "vector_service", fake)
    svc = IndexerService(vector_service=fake)
    assert svc.load_progress() == legacy._load_progress() == (7, {"a", "b"})


def test_prune_stale_delegates_to_store(monkeypatch):
    """prune_stale تمريرة رقيقة فوق prune_not_in الموجود."""
    fake = FakeVS(pruned=3)
    monkeypatch.setattr(legacy, "vector_service", fake)
    svc = IndexerService(vector_service=fake)
    active = {"k1", "k2"}
    assert svc.prune_stale(active) == 3
    assert fake.prune_arg == active
    assert svc.prune_stale(active) == fake.prune_not_in(active)
