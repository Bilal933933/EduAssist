"""بطارية تجميد سلوك grade المحلل — أي انحراف بعد مبادلة الكشف = فشل صريح.

القيم مثبتة من المخرجات الفعلية (2026-10-02)، بما فيها المراوغات:
الثانوي يُعامل primary، وبلا مرحلة يُفترض primary.
"""
from app.query_analyzer.analyzer import analyze

CASES = [
    ("حضر درس الفاعل للصف الخامس الابتدائي", {}, "primary_5", "known", "primary", "known"),
    ("اشرح المبتدأ للصف الثالث الإعدادي", {}, "prep_3", "known", "prep", "known"),
    ("الخامس", {"stage": "prep"}, "prep_5", "known", "prep", "known"),
    ("السادس", {"stage": "primary"}, "primary_6", "known", "primary", "known"),
    ("مراجعة نحو", {}, None, "unknown", None, "unknown"),
    ("درس الفاعل للصف الأول الثانوي", {}, "primary_1", "known", "primary", "known"),
    ("للصف الثاني", {}, "primary_2", "known", "primary", "known"),
    ("الصف الرابع الابتدائي", {}, "primary_4", "known", "primary", "known"),
    ("تحضير درس كان للصف السادس", {}, "primary_6", "known", "primary", "known"),
    ("أسئلة نحو", {}, None, "unknown", None, "unknown"),
    ("مراجعة للمرحلة الإعدادية", {}, None, "unknown", "prep", "inferred"),
    ("امتحان للصف الخامس الابتدائي", {}, "primary_5", "known", "primary", "known"),
    ("الصف الخامس", {}, "primary_5", "known", "primary", "known"),
    ("للصف الأول الإعدادي", {}, "prep_1", "known", "prep", "known"),
    ("حضر درس الحال للصف الثاني الإعدادي", {}, "prep_2", "known", "prep", "known"),
    ("حضر درس الفاعل للصف الخامس في المدرسة الإعدادية", {}, "prep_5", "known", "prep", "known"),
]


def test_grade_freeze():
    for question, ctx, grade, gstatus, stage, sstatus in CASES:
        scope = analyze(question, ctx).scope
        assert (scope.grade.value, scope.grade.status) == (grade, gstatus), question
        assert (scope.stage.value, scope.stage.status) == (stage, sstatus), question
