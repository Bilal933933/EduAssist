import json
import os
import re
from pathlib import Path

PAGE_ANCHOR = re.compile(r"\n##\s*صفحة\s+(\d+)\s*")
ENCODED_UNICODE = re.compile(r"#U([0-9A-Fa-f]{4,6})")

GRADE_NAMES = {
    "primary_1": "الصف الأول الابتدائي",
    "primary_4": "الصف الرابع الابتدائي",
    "primary_5": "الصف الخامس الابتدائي",
    "primary_6": "الصف السادس الابتدائي",
    "prep_1": "الصف الأول الإعدادي",
    "prep_2": "الصف الثاني الإعدادي",
    "prep_3": "الصف الثالث الإعدادي",
    "secondary_1": "الصف الأول الثانوي",
    "secondary_2": "الصف الثاني الثانوي",
    "secondary_3": "الصف الثالث الثانوي",
}


def decode_encoded_name(value: str) -> str:
    """يفك أسماء المجلدات المشفرة بصيغة #UXXXX دون تغيير الملفات على القرص."""
    if not value:
        return value
    return ENCODED_UNICODE.sub(lambda m: chr(int(m.group(1), 16)), value)


def _load_json(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _find_nearest_metadata(book_dir: str, stop_dir: str | None = None):
    """يعثر على أقرب metadata.json/meta.json بدءًا من المجلد الحالي إلى الجذر."""
    current = Path(book_dir).resolve()
    stop = Path(stop_dir).resolve() if stop_dir else None
    while True:
        for name in ("metadata.json", "meta.json"):
            path = current / name
            if path.exists():
                return _load_json(str(path)), str(path)
        if stop and current == stop:
            break
        if current.parent == current:
            break
        if stop and stop not in current.parents:
            break
        current = current.parent
    return {}, None


def _stage_from_grade(grade: str | None) -> str | None:
    if not grade:
        return None
    if grade.startswith("primary_"):
        return "primary"
    if grade.startswith("prep_"):
        return "prep"
    if grade.startswith("secondary_"):
        return "secondary"
    return None


def _content_ranges(metadata):
    ranges = []
    for part in metadata.get("parts", []):
        for s in part.get("sections", []):
            if s.get("kind") == "content":
                ranges.append((s.get("page"), s.get("endPage", s.get("page")), s))
    return ranges


def _section_meta_for_page(ranges, page):
    for p1, p2, section in ranges:
        if p1 is not None and p2 is not None and p1 <= page <= p2:
            return section
    return {}


SUBJECT_PATH_ALIASES = {
    "اللغة العربية": ["اللغة العربية", "اللغة-العربية", "عربي", "arabic"],
    "اللغة الإنجليزية": ["اللغة الإنجليزية", "اللغة-الإنجليزية", "اللغة الانجليزية", "اللغة-الإنجليزية", "english"],
    "الرياضيات": ["الرياضيات", "رياضيات", "math"],
    "العلوم": ["العلوم", "علوم", "science"],
    "الدراسات الاجتماعية": ["الدراسات الاجتماعية", "الدراسات-الاجتماعية", "دراسات اجتماعية", "دراسات-اجتماعية", "social"],
}


def _infer_subject_from_segments(segments):
    decoded = [decode_encoded_name(s).replace("-", " ").strip() for s in segments]
    for subject, aliases in SUBJECT_PATH_ALIASES.items():
        for segment in reversed(decoded):
            compact = segment.lower()
            if any(alias.lower() in compact for alias in aliases):
                return subject
    return None


def _slugify_id(value):
    value = decode_encoded_name(value or "").strip().lower()
    value = re.sub(r"[^\w\u0600-\u06ff]+", "-", value, flags=re.UNICODE).strip("-")
    return value[:120] or None


def _metadata_context(book_dir: str, segments: list[str], stop_dir: str):
    metadata, metadata_path = _find_nearest_metadata(book_dir, stop_dir)
    grade = segments[2] if len(segments) >= 3 and segments[1] in {"primary", "prep", "secondary"} else None
    stage = _stage_from_grade(grade) or metadata.get("stage")
    # pedagogy مصدر منفصل لا يخلط مع textbook/reference
    if segments and segments[0] == "pedagogy":
        source_type = "pedagogy"
    elif segments and segments[0] == "textbook":
        source_type = "textbook"
    else:
        source_type = metadata.get("source_type") or metadata.get("type") or "reference"
        if source_type == "general":
            source_type = "reference"
    # pedagogy قد يحدد grades مصفوفة في metadata
    if source_type == "pedagogy" and not grade and metadata.get("grades"):
        grades_meta = metadata.get("grades")
        if isinstance(grades_meta, list) and grades_meta:
            grade = grades_meta[0]
            stage = _stage_from_grade(grade) or stage or metadata.get("stage")
    inferred_subject = _infer_subject_from_segments(segments)
    return {
        "metadata": metadata,
        "metadata_path": metadata_path,
        "grade": grade,
        "stage": stage,
        "subject": metadata.get("subject") or inferred_subject,
        "branch": metadata.get("branch"),
        "source_type": source_type,
        "book_id": metadata.get("id") or _slugify_id("-".join(segments[1:])),
        "book_title": metadata.get("title"),
        "ranges": _content_ranges(metadata),
    }


def load_book(book_dir):
    metadata = _load_json(os.path.join(book_dir, "metadata.json"))
    ranges = _content_ranges(metadata)
    sections = []
    for part in metadata.get("parts", []):
        path = os.path.join(book_dir, part["file"])
        text = open(path, encoding="utf-8").read()
        pieces = PAGE_ANCHOR.split(text)
        for i in range(1, len(pieces), 2):
            page = int(pieces[i])
            body = pieces[i + 1].strip()
            if not body:
                continue
            section = _section_meta_for_page(ranges, page)
            if not section:
                continue
            sections.append({
                "title": section.get("title") or metadata.get("title", ""),
                "text": body,
                "source": metadata.get("title", ""),
                "page": page,
                "grade": None,
                "stage": metadata.get("stage"),
                "subject": metadata.get("subject"),
                "branch": metadata.get("branch"),
                "source_type": "textbook",
                "book_id": metadata.get("id"),
                "unit": part.get("chapter") or "",
                "lesson": section.get("title", ""),
                "concepts": section.get("concepts", []),
                "kind": section.get("kind", "content"),
                "doc_path": os.path.relpath(book_dir, Path(book_dir).parents[0]).replace(os.sep, "/"),
            })
    return sections


def _parse_front_matter(text):
    lines = text.lstrip("\ufeff").split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text
    meta = {}
    end = 1
    while end < len(lines) and lines[end].strip() != "---":
        idx = lines[end].find(":")
        if idx > 0:
            meta[lines[end][:idx].strip()] = lines[end][idx + 1:].strip()
        end += 1
    if end >= len(lines):
        return {}, text
    return meta, "\n".join(lines[end + 1:])


def _read_meta_title(book_dir):
    for name in ("metadata.json", "meta.json"):
        path = os.path.join(book_dir, name)
        if os.path.exists(path):
            data = _load_json(path)
            if data.get("title"):
                return data["title"]
    return None


def _h1_title(text):
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("##"):
            return stripped[2:].strip()
    return None


def _build_source(segments, fallback_title):
    """يبني label مقروءًا للمصدر دون استخدام أسماء #UXXXX المشفرة."""
    decoded = [decode_encoded_name(s) for s in segments]
    if "general" in decoded or len(decoded) < 3:
        return fallback_title
    grade_key = decoded[2]
    grade = GRADE_NAMES.get(grade_key, grade_key.replace("_", " "))
    parts = [grade]
    if len(decoded) > 3:
        parts.append(decoded[3].replace("-", " "))
    parts.extend(s.replace("-", " ") for s in decoded[4:])
    return " — ".join(p.strip() for p in parts if p.strip()) or fallback_title


def _load_simple_book(book_dir, segments, content_root=None):
    content_root = content_root or os.path.dirname(book_dir)
    context = _metadata_context(book_dir, segments, content_root)
    metadata = context["metadata"]
    meta_title = metadata.get("title") or _read_meta_title(book_dir)
    sections = []

    for name in sorted(os.listdir(book_dir)):
        path = os.path.join(book_dir, name)
        if not name.endswith(".md") or not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8-sig") as f:
            raw = f.read()
        meta, body = _parse_front_matter(raw)

        grade = meta.get("grade") or context["grade"]
        stage = _stage_from_grade(grade) or meta.get("stage") or context["stage"]
        subject = meta.get("subject") or context["subject"] or _infer_subject_from_segments(segments)
        branch = meta.get("course") or meta.get("branch") or context["branch"]
        if not branch and subject == "اللغة العربية":
            # مجلد فرعي مثل النحو/الصرف يمكنه تحديد الفرع دون اختلاق مادة أخرى.
            decoded_segments = [decode_encoded_name(x).replace("-", " ").strip() for x in segments]
            for candidate in ("نحو", "صرف", "بلاغة", "أدب", "قراءة", "نصوص"):
                if any(candidate in seg for seg in decoded_segments):
                    branch = candidate
                    break
        source_type = meta.get("type") or meta.get("source_type") or context["source_type"]
        if source_type == "general":
            source_type = "reference"
        # pedagogy يبقى pedagogy حتى لو front-matter يحدده صراحة
        if source_type not in ("textbook", "teacher_guide", "reference", "pedagogy", "general"):
            source_type = "reference"
        book_id = meta.get("book_id") or metadata.get("id") or context["book_id"]
        source = _build_source(segments, meta.get("title") or meta_title or name[:-3])
        title = meta.get("title") or meta_title or _h1_title(body) or decode_encoded_name(segments[-1]).replace("-", " ")
        doc_path = os.path.relpath(path, content_root).replace(os.sep, "/")

        pieces = PAGE_ANCHOR.split("\n" + body)
        if len(pieces) > 1:
            for i in range(1, len(pieces) - 1, 2):
                page = int(pieces[i])
                text = pieces[i + 1].strip()
                if not text:
                    continue
                section_meta = _section_meta_for_page(context["ranges"], page)
                # metadata.json wins over file/folder guesses for concepts/title.
                section_title = section_meta.get("title") or title
                sections.append({
                    "title": section_title,
                    "text": text,
                    "source": source,
                    "page": page,
                    "doc_path": doc_path,
                    "doc_type": source_type,
                    "grade": grade,
                    "stage": stage,
                    "subject": subject,
                    "branch": branch,
                    "source_type": source_type,
                    "book_id": book_id,
                    "unit": section_meta.get("unit") or metadata.get("unit") or "",
                    "lesson": section_meta.get("lesson") or section_title,
                    "concepts": section_meta.get("concepts") or metadata.get("concepts") or [],
                    "kind": section_meta.get("kind", "content"),
                })
        else:
            # ملفات دروس Markdown مثل almbtda-walkhbr-1.md
            raw_sections = re.split(r"\n##\s+", body)
            for chunk in raw_sections:
                chunk = chunk.strip()
                if not chunk:
                    continue
                lines = chunk.split("\n")
                sec_title = lines[0].strip() or title
                text = "\n".join(lines[1:]).strip()
                if not text:
                    continue
                sections.append({
                    "title": title if sec_title.startswith("#") else sec_title,
                    "text": text,
                    "source": source,
                    "doc_path": doc_path,
                    "doc_type": source_type,
                    "grade": grade,
                    "stage": stage,
                    "subject": subject,
                    "branch": branch,
                    "source_type": source_type,
                    "book_id": book_id,
                    "unit": metadata.get("unit") or "",
                    "lesson": title,
                    "concepts": metadata.get("concepts") or [],
                    "kind": "content",
                })
    return sections


def _iter_book_dirs(root):
    for entry in sorted(os.listdir(root)):
        book_dir = os.path.join(root, entry)
        if not os.path.isdir(book_dir):
            continue
        entries = os.listdir(book_dir)
        has_md = any(f.endswith(".md") and os.path.isfile(os.path.join(book_dir, f)) for f in entries)
        if has_md:
            yield book_dir
        else:
            yield from _iter_book_dirs(book_dir)
