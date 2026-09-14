import json, re

def generate_flashcards(client, hits: list, topic: str = "الفاعل") -> list:
    context = "\n".join(f"- {h.get('text','')[:250]}" for h in hits[:5])
    prompt = f"""ولّد 5 بطاقات استذكار (Flashcards) لدرس {topic} بناءً على:
{context}

أجب JSON فقط: {{"cards": [{{"q": "سؤال", "a": "جواب مختصر"}}]}}
"""
    try:
        from app.modules.lesson_knowledge.application.agent.fc_client import call_simple
        raw = call_simple(client, prompt, "أنت مولد بطاقات. JSON فقط.")
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m: return []
        return json.loads(m.group()).get("cards", [])[:5]
    except: return []

def generate_quiz(client, hits: list, topic: str = "الفاعل") -> list:
    context = "\n".join(f"- {h.get('text','')[:250]}" for h in hits[:5])
    prompt = f"""ولّد اختبار 5 أسئلة اختيار من متعدد لدرس {topic} بناءً على:
{context}

أجب JSON فقط: {{"quiz": [{{"q": "سؤال", "options": ["أ","ب","ج","د"], "answer": 0, "explain": "شرح"}}]}}
"""
    try:
        from app.modules.lesson_knowledge.application.agent.fc_client import call_simple
        raw = call_simple(client, prompt, "أنت مولد اختبارات. JSON فقط.")
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m: return []
        return json.loads(m.group()).get("quiz", [])[:5]
    except: return []
