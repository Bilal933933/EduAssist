import pathlib

PROMPT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent / "ai" / "prompts"

def _load(rel: str) -> str:
    p = PROMPT_ROOT / rel
    if p.exists():
        return p.read_text(encoding="utf-8").strip()
    return ""

def compose(analysis, evidence_text: str = "") -> tuple[str, str]:
    intent = analysis.intent
    stage = analysis.scope.stage.value or "prep"
    branch = analysis.scope.branch.value or "general"

    core = _load("core/system.md")
    intent_p = _load(f"intents/{intent}.md") or _load("intents/explain.md")
    grade_file = "prep.md" if stage in ("prep","secondary") else "primary.md"
    grade_p = _load(f"grades/{grade_file}")
    branch_files = {
        "نحو": "branches/grammar.md",
        "صرف": "branches/morphology.md",
        "بلاغة": "branches/rhetoric.md",
        "إملاء": "branches/spelling.md",
        "قراءة": "branches/reading.md",
        "نصوص": "branches/reading.md",
        "أدب": "branches/reading.md",
        "تعبير": "branches/expression.md",
    }
    branch_p = ""
    for key, rel in branch_files.items():
        if key in (branch or ""):
            branch_p = _load(rel)
            if branch_p:
                break
    citations = _load("shared/citations.md")
    evidence_header = _load("shared/evidence.md")

    # output contract حسب intent
    if intent == "prepare_lesson":
        output_p = _load("outputs/lesson_plan.md")
    elif intent == "compare":
        output_p = _load("outputs/table.md")
    else:
        output_p = ""

    # سياق منظم
    scope_ctx = f"الصف: {analysis.scope.grade.value or 'غير محدد'} | المرحلة: {stage} | الفرع: {branch} | السياسة: {analysis.source_policy} | المواضيع: {', '.join(analysis.topics)}"

    system = "\n\n".join(filter(None, [core, intent_p, grade_p, branch_p, citations, output_p]))
    user = f"[سياق] {scope_ctx}\n\n[أدلة]\n{evidence_text}\n\n[تعليمات] التزم بالأدلة فقط."
    return system, user
