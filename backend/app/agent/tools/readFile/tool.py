import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ALLOWED_ROOTS = [
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "books"),
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"),
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "content"),
    os.path.join(os.path.dirname(__file__), "..", "..", "content"),
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
        direct = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", path))
        if os.path.exists(direct):
            for r in ALLOWED_ROOTS:
                ar = os.path.abspath(r)
                if os.path.exists(ar) and direct.startswith(ar):
                    return direct
    raise FileNotFoundError(f"الملف غير موجود أو غير مسموح: {path}")

def _smart_read(content: str, path: str, query: str = "", max_chars: int = 8000) -> str:
    if content.lstrip().startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2]
    content = content.lstrip("\ufeff").strip()
    if len(content) <= max_chars and not query:
        return content
    sections = re.split(r'\n(?=#{1,3}\s)', content)
    sections = [s.strip() for s in sections if s.strip()]
    if not sections:
        return content[:max_chars] + "\n\n... (اقتطاع)"
    if query:
        q_norm = query.strip()
        scored = []
        for sec in sections:
            score = sum(1 for w in q_norm.split() if w in sec[:500])
            if score > 0:
                scored.append((score, sec))
        if scored:
            scored.sort(key=lambda x: -x[0])
            best = "\n\n".join(s for _, s in scored[:2])
            if len(best) > max_chars:
                best = best[:max_chars] + "\n\n... (اقتطاع القسم)"
            return f"[مقتطف من {os.path.basename(path)} - استعلام: {query}]\n\n{best}"
    toc = []
    for sec in sections[:10]:
        first_line = sec.split("\n")[0].strip()[:80]
        toc.append(f"- {first_line}")
    toc_text = "\n".join(toc)
    preview = "\n\n".join(sections[:2])[:max_chars - len(toc_text) - 100]
    return f"[فهرس {os.path.basename(path)} ({len(sections)} قسم)]\n{toc_text}\n\n---\n\n{preview}\n\n... (ملف كبير - حدد query لقراءة قسم محدد)"

def execute(args: dict, kb, client, inherited_scope=None):
    path = args.get("path", "")
    query = args.get("query", "")
    try:
        safe = _resolve_safe_path(path)
        with open(safe, encoding="utf-8-sig") as f:
            content = f.read()
        return _smart_read(content, safe, query)
    except Exception as e:
        return f"خطأ: {e}"
