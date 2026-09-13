from dataclasses import dataclass, field
from typing import Literal

ScopeStatus = Literal["known", "inferred", "unknown", "ambiguous"]

@dataclass
class ScopeField:
    value: str | None = None
    status: ScopeStatus = "unknown"

@dataclass
class Scope:
    stage: ScopeField = field(default_factory=ScopeField)   # primary/prep/secondary/general
    grade: ScopeField = field(default_factory=ScopeField)   # primary_5 / prep_2 ...
    subject: ScopeField = field(default_factory=ScopeField) # اللغة العربية
    branch: ScopeField = field(default_factory=ScopeField)  # نحو/صرف/بلاغة
    topic: str | None = None

    def to_filter_dict(self) -> dict:
        d = {}
        if self.grade.value: d["grade"] = self.grade.value
        if self.stage.value: d["stage"] = self.stage.value
        if self.subject.value: d["subject"] = self.subject.value
        if self.branch.value: d["branch"] = self.branch.value
        return d

    def is_unknown(self, field: str) -> bool:
        return getattr(self, field).status == "unknown"

    def needs_clarification(self, intent: str) -> tuple[bool, str | None]:
        # قاعدة: اسأل فقط إذا كان النقص يغير الناتج مادياً
        if intent == "prepare_lesson" and self.is_unknown("grade"):
            return True, "لأي صف تريد تحضير الدرس؟"
        if intent in ("generate_exam", "generate_exercises") and self.is_unknown("grade"):
            # لتدريبات/امتحان بدون صف → لا نوقف، نستخدم مراجع عامة
            return False, None
        if intent == "explain" and self.is_unknown("grade"):
            return False, None
        return False, None
