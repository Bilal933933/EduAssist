import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ALLOWED_ROOTS = [
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "books"),
    os.path.join(os.path.dirname(__file__), "..", "..", "data"),
    os.path.join(os.path.dirname(__file__), "..", "..", "content"),
    os.path.join(os.path.dirname(__file__), "..", "content"),
]

# Function Calling Schema الرسمي لـ Gemini
TOOL_DECLARATIONS = [
    {
        "name": "searchChunks",
        "description": "ابحث في مصادر المدرس (كتب ومنهج ومراجع نحو). استخدمه للحصول على قواعد وأمثلة.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "نص البحث العربي، مثال: الفاعل علامات رفعه"},
                "top_k": {"type": "integer", "description": "عدد النتائج النهائية بعد الدمج (من 5 إلى 20)"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "readFile",
        "description": "اقرأ ملف Markdown من content أو data. يعيد فهرس الأقسام إذا كان كبيراً، أو القسم المطلوب إذا حددت query.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "مسار الملف مثل content/textbook/primary/grade5/الفاعل.md أو data/books/madrasati/textbook/primary/.../part-01.md"},
                "query": {"type": "string", "description": "اختياري: موضوع تبحث عنه داخل الملف، مثال: الفاعل. يعيد القسم المطابق فقط"}
            },
            "required": ["path"]
        }
    }
]


def _resolve_safe_path(path: str) -> str:
    path = path.replace("\\", "/").strip()
    if ".." in path:
        raise ValueError(f"مسار غير مسموح: {path}")
    for root in ALLOWED_ROOTS:
        abs_root = os.path.abspath(root)
        if not os.path.exists(abs_root):
            continue
        candidate = os.path.abspath(os.path.join(abs_root, path.lstrip("/")))
        if os.path.exists(candidate) and candidate.startswith(abs_root):
            return candidate
        direct = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", path))
        if os.path.exists(direct):
            for r in ALLOWED_ROOTS:
                ar = os.path.abspath(r)
                if os.path.exists(ar) and direct.startswith(ar):
                    return direct
    raise FileNotFoundError(f"الملف غير موجود أو غير مسموح: {path}")


import re

def _smart_read(content: str, path: str, query: str = "", max_chars: int = 8000) -> str:
    """قراءة ذكية: تفهم هيكلة المنهج (content/textbook، front-matter، ## عناوين)."""
    # 1. إزالة front-matter
    if content.lstrip().startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2]
    content = content.lstrip("\ufeff").strip()

    # 2. إذا صغير، أعده كاملاً
    if len(content) <= max_chars and not query:
        return content

    # 3. قسم حسب العناوين (## و #)
    sections = re.split(r'\n(?=#{1,3}\s)', content)
    sections = [s.strip() for s in sections if s.strip()]

    if not sections:
        return content[:max_chars] + "\n\n... (اقتطاع)"

    # 4. إذا يوجد query، ابحث عن القسم المطابق
    if query:
        q_norm = query.strip()
        scored = []
        for sec in sections:
            # درجة بسيطة: وجود كلمات الاستعلام في العنوان/النص
            score = sum(1 for w in q_norm.split() if w in sec[:500])
            if score > 0:
                scored.append((score, sec))
        if scored:
            scored.sort(key=lambda x: -x[0])
            # أعد أفضل قسمين مطابقين
            best = "\n\n".join(s for _, s in scored[:2])
            if len(best) > max_chars:
                best = best[:max_chars] + "\n\n... (اقتطاع القسم)"
            return f"[مقتطف من {os.path.basename(path)} - استعلام: {query}]\n\n{best}"

    # 5. بدون query وملف كبير: أعد فهرس + أول قسمين
    toc = []
    for sec in sections[:10]:
        first_line = sec.split("\n")[0].strip()[:80]
        toc.append(f"- {first_line}")
    toc_text = "\n".join(toc)
    preview = "\n\n".join(sections[:2])[:max_chars - len(toc_text) - 100]
    return f"[فهرس {os.path.basename(path)} ({len(sections)} قسم)]\n{toc_text}\n\n---\n\n{preview}\n\n... (ملف كبير - حدد query لقراءة قسم محدد)"


def execute_tool(name: str, args: dict, kb, client, inherited_scope: dict | None = None):
    """ينفذ أداة ويعيد observation كـ نص أو قائمة hits مع تمرير query_text للميتاداتا."""
    if name == "searchChunks":
        query = args.get("query", "")
        top_k = int(args.get("top_k", 5))
        from src.agent.chat import embed_question
        try:
            # Lazy: التضمين فقط عند fallback الضعيف داخل hybrid_search
            hits = kb.hybrid_search(query, None, top_k=top_k, scope=inherited_scope, candidate_k=40, fused_k=20, embed_fn=lambda: embed_question(client, query))
            return hits
        except Exception as e:
            return [{"error": str(e), "title": "خطأ", "text": ""}]
    elif name == "readFile":
        path = args.get("path", "")
        query = args.get("query", "")
        try:
            safe = _resolve_safe_path(path)
            with open(safe, encoding="utf-8-sig") as f:
                content = f.read()
            return _smart_read(content, safe, query)
        except Exception as e:
            return f"خطأ: {e}"
    else:
        return f"أداة غير معروفة: {name}"


def format_search_observation(hits: list[dict], max_hits: int = 8, max_chars: int = 600) -> str:
    """يحّول نتائج retrieval إلى evidence قابلة للقراءة من الـAgent."""
    if not hits:
        return "لا توجد نتائج بحث."
    blocks = []
    for i, hit in enumerate(hits[:max_hits], start=1):
        meta = " | ".join(
            x for x in [
                f"المصدر={hit.get('source') or 'غير محدد'}",
                f"الصف={hit.get('grade') or 'عام'}",
                f"المادة={hit.get('subject') or 'غير محددة'}",
                f"الفرع={hit.get('branch') or '-'}",
                f"الوحدة={hit.get('unit') or '-'}",
                f"الدرس={hit.get('lesson') or hit.get('title') or '-'}",
                f"الصفحة={hit.get('page') or '-'}",
            ]
            if x
        )
        evidence = (hit.get("text") or "").strip()
        if len(evidence) > max_chars:
            evidence = evidence[:max_chars].rstrip() + "…"
        blocks.append(f"[{i}] {meta}\n{evidence}")
    remaining = max(0, len(hits) - max_hits)
    suffix = f"\n(+ {remaining} مرشحًا إضافيًا في candidate pool)" if remaining else ""
    return "\n\n---\n\n".join(blocks) + suffix
