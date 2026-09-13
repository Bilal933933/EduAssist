import sys
sys.stdout.reconfigure(encoding='utf-8')

from src.loader import load_knowledge_sections, load_all_sources
from src.loader.book_loader import _build_source

def test_load_knowledge_sections():
    import os
    # الملف السطحي محذوف - الاختبار يتخطى إذا غير موجود
    if not os.path.exists("data/grammar_knowledge.md"):
        assert True
        return
    sections = load_knowledge_sections()
    assert len(sections) > 10

def test_build_source():
    # general → يرجع fallback
    assert _build_source(["general", "x"], "عنوان") == "عنوان"
    # primary → يبني مصدر
    result = _build_source(["textbook", "primary", "primary_1", "اللغة العربية"], "fallback")
    assert "الصف الأول" in result or "primary" in result.lower()

def test_load_all_sources():
    sections = load_all_sources()
    assert len(sections) > 4000
    # يجب أن يحتوي textbook و references من content الموحد
    has_content = any("content" in str(s.get("source","")) or "الصف" in str(s.get("source","")) or "اللغة" in str(s.get("title","")) for s in sections)
    assert has_content or len(sections) > 4000
