import importlib.util, pathlib
_spec = importlib.util.spec_from_file_location("clarifier_p0", str(pathlib.Path(__file__).resolve().parents[1] / "app" / "agent" / "clarifier.py"))
_clarifier = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_clarifier)
extract_scope = _clarifier.extract_scope
from src.loader.book_loader import decode_encoded_name, _parse_front_matter
from src.knowledge.hybrid import rrf_fuse


def test_extract_primary_grade_and_subject():
    scope = extract_scope("حضّر لي درس الفاعل للصف الخامس الابتدائي في اللغة العربية")
    assert scope["grade"] == "primary_5"
    assert scope["stage"] == "primary"
    assert scope["subject"] == "اللغة العربية"


def test_extract_prep_grade_and_branch():
    scope = extract_scope("مراجعة النحو للصف الثالث الإعدادي")
    assert scope["grade"] == "prep_3"
    assert scope["subject"] == "اللغة العربية"
    assert scope["branch"] == "نحو"


def test_decode_encoded_filename():
    assert decode_encoded_name("#U0627#U0644#U0644#U063a#U0629") == "اللغة"


def test_front_matter_preserved():
    meta, body = _parse_front_matter("---\ngrade: primary_4\nsubject: اللغة العربية\ncourse: النحو\ntype: textbook\n---\n## الجملة الاسمية\nالنص")
    assert meta["grade"] == "primary_4"
    assert meta["subject"] == "اللغة العربية"
    assert meta["course"] == "النحو"
    assert meta["type"] == "textbook"
    assert "الجملة الاسمية" in body


def test_scope_where_clause_compiles_grade_and_subject():
    from src.knowledge.search import _where_clause
    clause = _where_clause({"grade": "primary_5", "subject": "اللغة العربية"})
    sql = str(clause.compile(compile_kwargs={"literal_binds": True}))
    assert "grade" in sql
    assert "subject" in sql
    assert "primary_5" in sql
    assert "اللغة العربية" in sql
