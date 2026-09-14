import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.modules.lesson_knowledge.application.agent.tools import _smart_read, TOOL_DECLARATIONS, execute_tool
from unittest.mock import MagicMock

def test_tool_declarations():
    assert len(TOOL_DECLARATIONS) == 2
    names = [t["name"] for t in TOOL_DECLARATIONS]
    assert "searchChunks" in names
    assert "readFile" in names
    # readFile يجب أن يدعم query اختياري (1.4)
    read_decl = next(t for t in TOOL_DECLARATIONS if t["name"] == "readFile")
    assert "query" in read_decl["parameters"]["properties"]

def test_smart_read_small():
    content = "# عنوان\n## قسم1\nنص قصير"
    result = _smart_read(content, "test.md", "", 8000)
    assert "نص قصير" in result

def test_smart_read_large_without_query():
    content = ("# درس\n## قسم1\nنص1\n" + "كلمة " * 500) * 10
    result = _smart_read(content, "big.md", "", 1000)
    assert "فهرس big.md" in result
    assert "ملف كبير" in result

def test_smart_read_with_query():
    content = """---
title: الفاعل
---
# درس الفاعل
## تعريف الفاعل
الفاعل اسم مرفوع
## علامات رفع الفاعل
الضمة للمفرد
## أمثلة
جاء الطالب
"""
    result = _smart_read(content, "test.md", "علامات رفع الفاعل", 2000)
    assert "علامات رفع الفاعل" in result
    assert "الضمة للمفرد" in result

def test_execute_readFile_real():
    kb = MagicMock()
    client = MagicMock()
    result = execute_tool("readFile", {"path": "content/textbook/primary/primary_1/اللغة العربية/part-01.md", "query": "الفاعل"}, kb, client)
    assert len(result) > 20  # ملف موجود في content الموحد
