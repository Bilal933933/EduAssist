import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from google import genai

try:
    from app.agent.chat import ask
    from src.knowledge.embeddings import embed_question
    from src.knowledge_base import KnowledgeBase
except ImportError:
    from agent.chat import ask
    from knowledge.embeddings import embed_question
    from knowledge_base import KnowledgeBase

load_dotenv()

# تهيئة قاعدة البيانات المتجهية (إذا لم تكن مفهرسة، ستفشل KnowledgeBase)
try:
    kb = KnowledgeBase()
except SystemExit as e:
    print(e)
    sys.exit(1)


def main():
    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit("GEMINI_API_KEY غير مضبوطة في .env")

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    print("مساعد النحو العربي — يبحث في قاعدة المعرفة ثم يجيب عبر Gemini")
    print("اكتب سؤالك، أو (خروج) للإنهاء.\n")

    while True:
        question = input("أنت: ").strip()
        if question.lower() in ("خروج", "exit", "quit"):
            break
        if not question:
            continue

        hits = kb.hybrid_search(question, None, embed_fn=lambda: embed_question(client, question))
        try:
            answer = ask(client, question, hits)
        except Exception as error:
            code = getattr(error, "code", "")
            if code == 429:
                print("\n(وصلت لحصة Gemini اليومية المجانية. أعد المحاولة غداً، "
                      "أو اضبط GEMINI_MODEL على نموذج آخر في .env)\n")
            else:
                print(f"\n(خطأ أثناء الاستدعاء: {error})\n")
            continue

        print("\nالمعرفة المسترجعة:")
        for h in hits:
            src = f" — {h['source']} صفحة {h['page']}" if h.get("source") else ""
            print(f"  - [{h['title']}]{src} (تشابه {h['similarity']:.2f})")
        print(f"\nالمساعد: {answer}\n")


if __name__ == "__main__":
    main()