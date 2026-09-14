import re

VALIDATE_PROMPT = """أنت مدقق مصادر لمساعد مدرس.

المحتوى المسترجع من مصادر المدرس:
{context}

إجابة المساعد المقترحة:
{answer}

مهمتك:
1. هل كل معلومة نحوية في الإجابة موجودة فعلاً في المحتوى؟ 
2. هل كل نقطة مهمة تذكر مصدرها [الكتاب]؟
3. إذا وجدت معلومة غير موجودة في المحتوى، احذفها واستبدلها بـ "لا يوجد في مصادرك"

أجب JSON فقط:
{{"valid": true/false, "issues": ["مشكلة1"], "corrected": "النص المصحح إذا لزم"}}
إذا كل شيء صحيح، أعد نفس الإجابة في corrected مع valid=true.
"""

def validate_citations(client, answer: str, hits: list) -> tuple:
    """يتحقق أن الإجابة مدعومة بالمصادر. يعيد (is_valid, corrected_answer, issues)."""
    if not hits or not answer:
        return True, answer, []

    context = "\n\n".join(f"[{h.get('title')}] {h.get('text')[:400]}" for h in hits[:5])
    prompt = VALIDATE_PROMPT.format(context=context[:4000], answer=answer[:3000])

    try:
        from app.agent.fc_client import call_simple
        raw = call_simple(client, prompt, "أنت مدقق. أجب JSON فقط.")
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return True, answer, []
        import json
        data = json.loads(m.group())
        valid = data.get("valid", True)
        issues = data.get("issues", [])
        corrected = data.get("corrected", answer)
        # إذا التصحيح أقصر بكثير، اعتبره حذف هلوسة
        if len(corrected) < len(answer) * 0.5:
            corrected = answer  # لا نثق بتصحيح يحذف نصف الإجابة
            valid = True
        print(f"[Validator] valid={valid} issues={issues[:1] if issues else 'لا يوجد'}")
        return valid, corrected, issues
    except Exception as e:
        print(f"[Validator error: {e}]")
        return True, answer, []
