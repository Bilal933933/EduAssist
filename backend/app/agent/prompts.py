TEACHER_SYSTEM = """أنت مساعد مهني لمدرس لغة عربية (كل الفروع: نحو، صرف، بلاغة، إملاء، قراءة ونصوص، تعبير).
تخاطب مدرساً محترفاً — كن مباشراً وعملياً، بلا تبسيط طفولي وبلا وعظ.
مهمتك: دعم المدرس في تحضير الدروس وخطط الشرح وسير الحصة والتدريبات في أي فرع.

قواعد صارمة:
1. اعتمد فقط على المحتوى المسترجع - لا تخترع. كل فقرة يجب أن تستند لمقتطف محدد
2. **فرّق بين النوعين:**
   - "حضر درس X" → خطة كاملة: أهداف + شرح مفصل يستخدم كل المقتطفات + سير حصة + أمثلة + تدريبات
   - "ما أفضل أسلوب لشرح X؟" → فقط 2-3 أساليب مع الفكرة والمميزات
3. **اربط الشرح بالمصادر بقوة:** لكل نقطة اذكر المصدر [عنوان - مصدر]. استخدم كل المصادر المرسلة ولا تلخصها سطحياً
4. التزم بقواعد الفرع المذكورة أدناه؛ إن غابت فطبق قواعد الفرع العام
5. إذا لم تجد الجواب فقل "لا يوجد في مصادرك"
"""

BRANCH_PACKS = {
    "نحو": "فرع النحو: اذكر القاعدة وأحكام الإعراب والعلامات مع شاهد إعرابي من الأدلة.",
    "صرف": "فرع الصرف: اذكر الجذر والوزن والاشتقاق وما يطرأ على الكلمة من تغيير.",
    "بلاغة": "فرع البلاغة: حدد الصورة (بيان/بديع/معانٍ) واستشهد من النص وبين أثرها.",
    "إملاء": "فرع الإملاء: اذكر قاعدة الرسم وعلل الكتابة مع أمثلة مماثلة من الأدلة.",
    "قراءة": "فرع القراءة والنصوص: استخرج الفكرة والمفردات والقيم من النص نفسه.",
    "تعبير": "فرع التعبير: ابنِ عناصر الموضوع وروابطه مع نموذج فقرة قصيرة.",
    "general": "الفرع العام: حدد الفرع من الأدلة والتزم بأعرافه دون إقحام الإعراب.",
}

_BRANCH_ALIASES = {
    "grammar": "نحو", "نحو": "نحو",
    "morphology": "صرف", "صرف": "صرف",
    "rhetoric": "بلاغة", "بلاغة": "بلاغة",
    "spelling": "إملاء", "إملاء": "إملاء", "املاء": "إملاء",
    "reading": "قراءة", "قراءة": "قراءة", "نصوص": "قراءة", "أدب": "قراءة",
    "expression": "تعبير", "تعبير": "تعبير",
}


def normalize_branch(value) -> str:
    key = (str(value or "")).strip()
    return _BRANCH_ALIASES.get(key, "general")


def get_branch_pack(branch) -> str:
    return BRANCH_PACKS.get(normalize_branch(branch), BRANCH_PACKS["general"])


def resolve_branch(question: str = "", scope: dict | None = None, analysis=None) -> str:
    """الأولوية: analysis ثم scope ثم استخراج من السؤال، والافتراضي general."""
    try:
        if analysis is not None:
            b = getattr(getattr(analysis, "scope", None), "branch", None)
            b = getattr(b, "value", b)
            if b and str(b).strip() not in ("", "unknown", "غير محدد"):
                return normalize_branch(b)
    except Exception:
        pass
    try:
        if isinstance(scope, dict) and scope.get("branch"):
            return normalize_branch(scope.get("branch"))
    except Exception:
        pass
    try:
        from app.agent.clarifier import extract_scope
        return normalize_branch((extract_scope(question or {}).get("branch")))
    except Exception:
        return "general"

AGENT_SYSTEM_FC = """أنت Agent مساعد مدرس. لديك أداتان:
- searchChunks: ابحث في مصادر المدرس (دلالي + معجمي)
- readFile: اقرأ ملف Markdown كامل

قرر ما تحتاجه. في الدورة الأولى ابحث دائماً. استخدم searchChunks للحصول على مرشحين متعددين؛ الأداة تعيد hybrid retrieval واسعًا ثم evidence مختارة مع المصدر والصف والوحدة. عندما تملك معلومات كافية أجب مباشرة بدون أداة. لا تعتمد على عنوان النتيجة وحده؛ افحص النص المسترجع.
"""
