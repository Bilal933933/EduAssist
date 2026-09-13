"""بوابة صلة الأدلة: نقد المسترجع قبل التوليد + بحث موجه للمحاور الناقصة."""
import json
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

# حدود الحكم: مكالمة واحدة لأعلى 24 (حصة مجانية محدودة — كل حكم إضافي يخاطر بـ 429)
BATCH_SIZE = 20
MAX_BATCHES = 2
SNIPPET_CHARS = 250
MIN_KEEPS = 5

CRITIC_PROMPT = """أنت ناقد صلة أدلة لمدرس لغة عربية. لا تجب عن السؤال، فقط احكم على الأدلة.

طلب المدرس: "{question}"

الأدلة (رقم - عنوان - مصدر - فرع - مقتطف):
{evidence}

أجب JSON فقط:
{{"keep": [أرقام الصالحة], "drop": [أرقام الفاسدة], "missing": ["محور ناقص"], "next_queries": ["استعلام بحث"], "proceed": true/false}}

قواعد:
- الصالح = يعالج نفس موضوع الطلب ولنفس المرحلة تقريباً.
- أبقِ المحاور المتكاملة: عناوين مختلفة لنفس الموضوع (تعريف/أحكام/عامل/أمثلة) تُحفظ معاً ولا تُسقط كمكررة.
- المراجع عند غياب المنهج: بسّط بدل أن تُسقط — لا تسقط دليلاً صالح الموضوع بحجة تقدم مستواه إذا لم يوجد بديل منهجي.
- أسقط فقط: فرع مختلف تماماً (بلاغة/صرف لطلب نحو)، تدريبات عن موضوع آخر لا علاقة له.
- المحاور المطلوبة أدناه خط أحمر: لا تسقط دليلاً يغطي أحدها ولو كان مستواه أعلى — المولد سيبسطه.
المحاور المطلوبة: {pillars}
- missing = محاور معرفية ناقصة (أسماء مفاهيم، مثال: الفاعل) لا صياغة الطلب.
- next_queries = استعلامات محددة لسد الناقص فقط، وإلا [].
- proceed = false إذا بقي أقل من 3 صالحة أو محور أساسي ناقص مع وجود next_queries.
"""


def _ev_lines(hits: list, offset: int = 0) -> str:
    lines = []
    for j, h in enumerate(hits):
        i = offset + j
        lines.append(
            f"{i} - {h.get('title', '?')} | {h.get('source', '?')} "
            f"| فرع:{h.get('branch') or '-'} | ص:{h.get('page') or '-'} | "
            f"{(h.get('text') or '')[:SNIPPET_CHARS]}"
        )
    return "\n".join(lines)


def _titles(hits: list, idxs: list) -> list:
    out = []
    for i in idxs:
        if isinstance(i, int) and 0 <= i < len(hits):
            t = str(hits[i].get("title") or "?")[:60]
            p = hits[i].get("page")
            out.append(f"{t} ص{p}" if p else t)
    return out


def judge_relevance(client, question: str, hits: list, pillars: list | None = None) -> dict:
    """حكم LLM على الصلة دفعاتٍ. fail-open: أي فشل يعيد الكل مع proceed=True."""
    n = len(hits)
    if n == 0:
        return {"keep": [], "drop": [], "missing": [], "next_queries": [question],
                "proceed": False, "kept_titles": [], "dropped_titles": [], "unjudged": 0,
                "restored_titles": []}
    judged = hits[:BATCH_SIZE * MAX_BATCHES]
    unjudged = n - len(judged)
    keep, drop, missing, queries = [], [], [], []
    proceed = True
    pillars_txt = "، ".join(pillars or []) or "غير محددة"
    try:
        from src.agent.fc_client import call_simple
        for b in range(0, len(judged), BATCH_SIZE):
            batch = judged[b:b + BATCH_SIZE]
            raw = call_simple(
                client,
                CRITIC_PROMPT.format(question=(question or "")[:300], pillars=pillars_txt,
                                     evidence=_ev_lines(batch, b)),
                "أنت ناقد صلة أدلة. أجب JSON فقط.",
            )
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            if not m:
                keep.extend(range(b, b + len(batch)))
                continue
            data = json.loads(m.group())
            nb = b + len(batch)
            keep.extend([i for i in data.get("keep", []) if isinstance(i, int) and b <= i < nb])
            drop.extend([i for i in data.get("drop", []) if isinstance(i, int) and b <= i < nb])
            missing.extend([str(x)[:80] for x in data.get("missing", [])][:4])
            queries.extend([str(x)[:120] for x in data.get("next_queries", [])][:2])
            if not data.get("proceed", True):
                proceed = False
        if not keep:
            raise ValueError("empty keep")
        return {"keep": keep, "drop": drop, "missing": missing[:4], "next_queries": queries[:2],
                "proceed": proceed, "kept_titles": _titles(hits, keep),
                "dropped_titles": _titles(hits, drop), "unjudged": unjudged,
                "restored_titles": []}
    except Exception as e:
        print(f"[Critic fallback-open: {e}]")
        return {"keep": list(range(n)), "drop": [], "missing": [], "next_queries": [],
                "proceed": True, "kept_titles": [], "dropped_titles": [], "unjudged": 0,
                "restored_titles": []}


def _restore_floor(hits: list, kept: list, verdict: dict) -> tuple:
    """أرضية صلبة: استعادة أفضل المسقطات (نفس الفرع أولاً) حتى MIN_KEEPS."""
    if len(kept) >= MIN_KEEPS:
        return kept, []
    drop_idxs = [i for i in verdict.get("drop", []) if isinstance(i, int) and 0 <= i < len(hits)]
    kept_ids = {id(h) for h in kept}

    def branch_of(i):
        return str(hits[i].get("branch") or "")

    same = [i for i in drop_idxs if "نحو" in branch_of(i)]
    other = [i for i in drop_idxs if "نحو" not in branch_of(i)]
    restored = []
    for i in same + other:
        if len(kept) >= MIN_KEEPS:
            break
        if id(hits[i]) not in kept_ids:
            kept.append(hits[i])
            kept_ids.add(id(hits[i]))
            restored.append(i)
    if restored:
        print(f"[Critic] استعادة {len(restored)}: {_titles(hits, restored)}")
    return kept, restored


def judge_and_filter(client, question: str, hits: list, kb, scope, max_retries: int = 1,
                     pillars: list | None = None) -> tuple:
    """نقد دفعات + بحث موجه موسع حتى حد أدنى من الصوالح. يعيد (المصفاة, معلومات التتبع)."""
    from src.agent.tools import execute_tool

    verdict = judge_relevance(client, question, hits, pillars)
    kept = [hits[i] for i in verdict["keep"]]
    info = {"kept": len(kept), "dropped": len(verdict["drop"]),
            "missing": verdict["missing"], "proceed": verdict["proceed"],
            "retry": False, "kept_titles": verdict["kept_titles"],
            "dropped_titles": verdict["dropped_titles"], "unjudged": verdict["unjudged"],
            "restored_titles": []}

    retries = 0
    while (len(kept) < MIN_KEEPS or not verdict["proceed"]) \
            and verdict["next_queries"] and retries < max_retries:
        retries += 1
        extra = []
        for q in verdict["next_queries"][:2]:
            try:
                r = execute_tool("searchChunks", {"query": q, "top_k": 10}, kb, client, inherited_scope=scope)
                if isinstance(r, list):
                    extra.extend(r)
                    print(f"[Critic] بحث موجه '{q[:40]}' → {len(r)}")
            except Exception as e:
                print(f"[Critic research skip: {e}]")
        if not extra:
            break
        seen = {h.get("doc_key") or (h.get("text", "")[:120]) for h in hits}
        hits = list(hits) + [h for h in extra if (h.get("doc_key") or h.get("text", "")[:120]) not in seen]
        verdict = judge_relevance(client, question, hits, pillars)
        kept = [hits[i] for i in verdict["keep"]]
        info = {"kept": len(kept), "dropped": len(verdict["drop"]),
                "missing": verdict["missing"], "proceed": verdict["proceed"],
                "retry": True, "retries": retries, "kept_titles": verdict["kept_titles"],
                "dropped_titles": verdict["dropped_titles"], "unjudged": verdict["unjudged"],
                "restored_titles": []}
    kept, restored = _restore_floor(hits, kept, verdict)
    info["kept"] = len(kept)
    info["restored_titles"] = _titles(hits, restored)
    print(f"[Critic] صالح:{len(kept)} مسقط:{len(verdict['drop'])} مستعاد:{len(restored)} "
          f"غير_محكوم:{verdict['unjudged']} ناقص:{verdict['missing']}")
    if not kept:
        kept = hits  # لا نترك السياق فارغاً أبداً؛ المولد سيعلن النقص بصراحة
    return kept, info
