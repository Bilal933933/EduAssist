import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
KNOWLEDGE_PATH = os.path.join(DATA_DIR, "grammar_knowledge.md")

def load_knowledge_sections(path=KNOWLEDGE_PATH):
    """يقرأ ملف الملخص النحوي ويقسمه إلى أقسام حسب العناوين (##)."""
    with open(path, encoding="utf-8") as f:
        content = f.read()
    sections = []
    for section in re.split(r"\n##\s+", content):
        section = section.strip()
        if not section:
            continue
        lines = section.split("\n")
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        if body:
            sections.append({"title": title, "text": body, "source": "ملخص النحو"})
    return sections
