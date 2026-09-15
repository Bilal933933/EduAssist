"""تقييم Ragas مبسط: Faithfulness + Relevance عبر Gemini."""
import re
import json

EVAL_PROMPT = """قيّم هذه الإجابة:

سؤال المدرس: "{question}"
الإجابة: "{answer}"
المصادر:
{context}

قيّم 0-10:
- Faithfulness: هل كل جملة في الإجابة مدعومة حرفياً بالمصادر؟ (10=كلها مدعومة، 0=هلوسة)
- Relevance: هل أجابت السؤال مباشرة بدون حشو؟ (10=مباشرة، 0=خارج الموضوع)

أجب JSON فقط: {{"faithfulness": 8, "relevance": 9, "reason": "..."}}
"""

def evaluate(client, question: str, answer: str, hits: list) -> dict:
    context = "\n".join(f"- {h.get('text','')[:250]}" for h in hits[:4])
    prompt = EVAL_PROMPT.format(question=question, answer=answer[:2000], context=context)
    try:
        from app.agent.fc_client import call_simple
        raw = call_simple(client, prompt, "أنت مقيّم. أجب JSON فقط.")
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return {"faithfulness": 5, "relevance": 5, "reason": "فشل التحليل"}
        data = json.loads(m.group())
        faith = int(data.get("faithfulness", 5)) / 10
        relev = int(data.get("relevance", 5)) / 10
        print(f"[Ragas] faith={faith:.1f} relev={relev:.1f} - {data.get('reason','')[:60]}")
        return {"faithfulness": faith, "relevance": relev, "reason": data.get("reason",""), "raw": data}
    except Exception as e:
        print(f"[Ragas skip: {e}]")
        return {"faithfulness": 0.5, "relevance": 0.5, "reason": str(e)}
