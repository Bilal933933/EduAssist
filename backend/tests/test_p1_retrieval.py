from src.loader.semantic_chunker import split_semantic, chunk_sections_semantic
from src.knowledge.hybrid import rrf_fuse
from app.agent.tools import format_search_observation


def _words(n):
    return " ".join(f"كلمة{i}" for i in range(n))


def test_chunking_never_exceeds_max_tokens():
    text = "\n\n".join([_words(120) + "." for _ in range(5)])
    chunks = split_semantic(text, target_tokens=400, min_tokens=300, max_tokens=500, overlap_tokens=60)
    assert len(chunks) >= 2
    assert max(len(c.split()) for c in chunks) <= 500


def test_chunking_preserves_section_metadata():
    sections = [{
        "title": "الفاعل",
        "text": _words(700),
        "grade": "primary_5",
        "stage": "primary",
        "subject": "اللغة العربية",
        "branch": "نحو",
        "unit": "الوحدة الأولى",
        "lesson": "الفاعل",
        "concepts": ["فاعل", "مرفوع"],
        "book_id": "arabic-g5",
    }]
    chunks = chunk_sections_semantic(sections)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert chunk["grade"] == "primary_5"
        assert chunk["subject"] == "اللغة العربية"
        assert chunk["lesson"] == "الفاعل"
        assert chunk["concepts"] == ["فاعل", "مرفوع"]
        assert chunk["chunk_token_count"] == len(chunk["text"].split())


def test_rrf_accepts_large_candidate_pool_and_returns_requested_fused_size():
    semantic = [{"doc_key": f"d{i}", "text": f"semantic {i}"} for i in range(40)]
    lexical = [{"doc_key": f"d{i}", "text": f"lexical {i}"} for i in range(40)]
    fused = rrf_fuse(semantic, lexical, top_k=20)
    assert len(fused) == 20
    assert fused[0]["doc_key"] == "d0"


def test_agent_observation_contains_real_evidence_and_metadata():
    hits = [{
        "doc_key": "d1",
        "title": "علامات رفع الفاعل",
        "text": "الفاعل اسم مرفوع وعلامة رفعه الضمة في المفرد.",
        "source": "كتاب النحو",
        "page": 42,
        "grade": "primary_5",
        "subject": "اللغة العربية",
        "branch": "نحو",
        "unit": "الوحدة الأولى",
        "lesson": "الفاعل",
    }]
    obs = format_search_observation(hits)
    assert "الفاعل اسم مرفوع" in obs
    assert "الصف=primary_5" in obs
    assert "المصدر=كتاب النحو" in obs
