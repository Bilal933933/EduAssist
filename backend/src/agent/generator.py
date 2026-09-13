from src.agent.prompts import TEACHER_SYSTEM


def build_teacher_prompt(question, all_hits, history, file_contents, memory_block: str = ""):
    """يبني برومبت المدرس مع إمكانية حقن ذاكرة المدرس."""
    # لا ندخل candidate pool كاملًا في prompt؛ بعد rerank نرسل أفضل 5–8 evidence فقط.
    context_hits = list(all_hits or [])[:8]
    seen = set()
    parts = []
    for h in context_hits:
        key = (h.get("title"), h.get("text", "")[:50])
        if key in seen:
            continue
        seen.add(key)
        src = h.get("source", "مصدر")
        page = f" ص{h.get('page')}" if h.get("page") else ""
        parts.append(f"[{h.get('title')} - {src}{page}]\n{h.get('text')}")
    for path, content in (file_contents or {}).items():
        parts.append(f"[ملف: {path}]\n{content[:4000]}")
    context = "\n\n---\n\n".join(parts) if parts else "لا يوجد محتوى"
    hist = ""
    if history:
        hist = "\n".join(
            f"{'المدرس' if r == 'user' else 'المساعد'}: {t}" for r, t in history
        )
        hist = f"المحادثة السابقة:\n{hist}\n\n"
    is_style = any(
        k in question for k in ["أسلوب", "طريقة مشوقة", "كيف أشرح", "اقترح"]
    )
    if is_style:
        task = (
            "قدم فقط 2-3 أساليب مشوقة مع الفكرة والمميزات باختصار. "
            "لا تضف أهداف ولا سير حصة."
        )
    else:
        task = (
            "قدم خطة كاملة احترافية: أهداف + شرح عميق يربط كل نقطة بمقتطفها ونسبته "
            "+ سير حصة مفصل + أمثلة حرفية من المصادر + تدريبات. "
            "استخدم كل المقتطفات المرسلة ولا تلخصها سطحياً."
        )

    memory_section = f"{memory_block}\n\n" if memory_block else ""

    user = (
        f"{memory_section}{hist}"
        f"المحتوى المسترجع ({len(parts)} evidence مختارة بعد rerank):\n{context}\n\n"
        f"طلب المدرس: {question}\n"
        f"المطلوب: {task} اذكر المصدر عند الاستناد إلى معلومة، "
        f"ولا تذكر أي درجة تشابه داخل النص النهائي إلا إذا كانت متاحة فعلاً."
    )

    system = TEACHER_SYSTEM
    if memory_block:
        system = TEACHER_SYSTEM + "\n\n" + memory_block

    return system, user
