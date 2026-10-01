"""4 وكلاء فرعيين لتحضير الدرس - كل وكيل يبحث ويولد جزءه."""
from arabic_text import extract_topic, split_subtopics
from app.agent.tools import execute_tool
from app.agent.fc_client import call_simple
from app.agent.clarifier import extract_scope

SUB_TASKS = {
    "اهداف": "أهداف درس {topic} للصف {grade} (معرفية/مهارية/وجدانية)",
    "شرح": "شرح قاعدة {topic} مع تعريفه وأنواعه وعلامات إعرابه",
    "سير": "سير حصة {topic} (تمهيد 5د + عرض 15د + تطبيق 10د + تقويم 10د)",
    "تدريبات": "تدريبات وأمثلة على {topic} مع إجابات وعلامات إعراب",
}

def resolve_topic(question: str) -> str:
    """موضوع الدرس من نص الطلب — "النحو" عند الغياب."""
    return extract_topic(question) or "النحو"


def resolve_grade(question: str) -> str:
    """الصف لفظًا كما ورد — الافتراض الإعدادية عند الغياب (سياسة تحضير v1)."""
    import re
    if "إعدادي" in question or "إعدادية" in question:
        return "الثاني الإعدادي"
    if "ابتدائي" in question or "ابتدائية" in question:
        return "الخامس الابتدائي"
    if "ثانوي" in question or "ثانوية" in question:
        return "الثانوي"
    m = re.search(r'الصف\s+([^\s،,-]+)', question)
    if m:
        return m.group(1)
    return "المرحلة الإعدادية"


def run_sub_agents(client, kb, question: str) -> dict:
    """يشغل 4 وكلاء بالتوازي المنطقي ويعيد أجزاء الدرس."""
    topic, grade = resolve_topic(question), resolve_grade(question)
    inherited_scope = extract_scope(question)
    results = {}

    for key, template in SUB_TASKS.items():
        query = template.format(topic=topic, grade=grade)
        # كل وكيل يبحث عن 3 مقتطفات خاصة به
        hits = execute_tool("searchChunks", {"query": query, "top_k": 3}, kb, client, inherited_scope=inherited_scope)
        context = "\n".join(f"- {h.get('text','')[:300]} [{h.get('title')}]" for h in (hits or [])[:3])

        prompts = {
            "اهداف": f"اكتب 3 أهداف لدرس {topic} للصف {grade} بناءً على:\n{context}\nاختصر.",
            "شرح": f"اشرح قاعدة {topic} (تعريف/أنواع/علامات) بناءً على:\n{context}\nاذكر المصدر.",
            "سير": f"اكتب سير حصة {topic} (تمهيد/عرض/تطبيق/تقويم) بناءً على:\n{context}\nموجز.",
            "تدريبات": f"اكتب 3 تدريبات على {topic} مع إجابات بناءً على:\n{context}",
        }

        try:
            text = call_simple(client, prompts[key], "أنت وكيل متخصص. أجب باختصار واحترافية.")
            results[key] = {"text": text.strip(), "hits": hits}
            print(f"[SubAgent {key}] → {len(text)} حرف")
        except Exception as e:
            results[key] = {"text": f"تعذر توليد {key}: {e}", "hits": hits}
            print(f"[SubAgent {key} error: {e}]")

    return results, topic, grade

def synthesize_lesson(client, parts: dict, topic: str, grade: str) -> str:
    """يجمع 4 أجزاء في خطة نهائية موحدة."""
    import re
    combined = "\n\n".join(f"### {k}:\n{v['text']}" for k, v in parts.items())
    # الموضوع المركب (المبتدأ والخبر): قسم مستقل لكل جزء وإلا ابتلع أحدهما الآخر.
    cover = ""
    subtopics = split_subtopics(topic)
    if len(subtopics) > 1:
        cover = f" الموضوع مركب ({topic}): خصص قسمًا مستقلًا لكل جزء — {'، '.join(subtopics)} — وغطِّ تعريف كل جزء وأنواعه وأمثلته، ولا تدمجها في قسم واحد."
    prompt = f"اجمع هذه الأجزاء في خطة درس واحدة احترافية لـ {topic} الصف {grade} مع عناوين واضحة:\n{combined}\nلا تكرر، واذكر المصادر.{cover}"
    try:
        return call_simple(client, prompt, "أنت منسق خطط دروس. اجمع باحترافية.")
    except:
        return combined
