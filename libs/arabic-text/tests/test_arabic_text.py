"""اختبارات المكتبة المستقلة — تجمّد الحالات الميدانية المكتشفة."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from arabic_text import (
    extract_branch,
    extract_grade_code,
    extract_json_block,
    extract_subject,
    extract_topic,
    normalize_whitespace,
    parse_json_block,
    split_subtopics,
)


def test_topic_keeps_meem_and_ain():
    assert extract_topic("حضّر لي درس المبتدأ والخبر") == "المبتدأ والخبر"
    assert extract_topic("حضر درس الفاعل") == "الفاعل"
    assert extract_topic("درس المفعول به") == "المفعول به"
    assert extract_topic("درس المعرب والمبني") == "المعرب والمبني"


def test_topic_boundaries():
    assert extract_topic("درس المعرب والمبني للصف الخامس") == "المعرب والمبني"
    assert extract_topic("حضر لي درس الفاعل مع تدريبات") == "الفاعل"
    assert extract_topic("درس كان وأخواتها، الصف الثاني") == "كان وأخواتها"
    assert extract_topic("اشرح الفاعل؟") is None


def test_split_subtopics():
    assert split_subtopics("المبتدأ والخبر") == ["المبتدأ", "الخبر"]
    assert split_subtopics("كان وأخواتها") == ["كان", "أخواتها"]
    assert split_subtopics("الفاعل") == ["الفاعل"]
    assert split_subtopics("المؤول بالصريح") == ["المؤول بالصريح"]
    assert split_subtopics(None) == []
    assert split_subtopics("") == []


def test_grade_code():
    assert extract_grade_code("للصف الخامس الابتدائي") == ("primary_5", "primary")
    assert extract_grade_code("الصف الثالث الإعدادي") == ("prep_3", "prep")
    assert extract_grade_code("للصف الثاني") == ("primary_2", "primary")
    assert extract_grade_code("الصف الخامس") == ("primary_5", "primary")
    assert extract_grade_code("حضر درس الفاعل للصف الخامس في المدرسة الإعدادية") == ("prep_5", "prep")
    assert extract_grade_code("سؤال عام بلا صف") == (None, None)


def test_json_block():
    assert extract_json_block('نص {"ranking": [3, 1]} ذيل') == '{"ranking": [3, 1]}'
    assert extract_json_block("بلا أقواس") is None
    assert parse_json_block('{"a": 1}') == {"a": 1}
    assert parse_json_block("نص مكسور {") is None


def test_normalize():
    assert normalize_whitespace("  أهلا   بك ") == "أهلا بك"
    assert normalize_whitespace(None) == ""


def test_subject_branch_atoms():
    assert extract_subject("مراجعة الرياضيات") == "الرياضيات"
    assert extract_subject("سؤال عام") is None
    assert extract_branch("شرح النحو") == "نحو"
    assert extract_branch("الفاعل في الجملة") == "نحو"
    assert extract_branch("موضوع بلا فرع") is None
