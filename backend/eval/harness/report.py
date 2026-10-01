"""التقرير — JSON للتراكم وMarkdown للقراءة."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def save(adapter_name: str, results: list, summary: dict, out_dir: Path, commit: str = "unknown", repeats: int = 1, pin_model: str | None = None) -> dict:
    """يحفظ التقرير ويعيد المسارات."""
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    payload = {
        "harness_version": "v2",
        "adapter": adapter_name,
        "commit": commit,
        "repeats": repeats,
        "pin_model": pin_model,
        "deterministic": {"temperature": 0.0, "top_p": 1.0, "seed": 42},
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "results": results,
    }
    json_path = out_dir / f"intent_{adapter_name}_{stamp}.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    lines = [
        f"# تقرير النية — {adapter_name}",
        "",
        f"- الحالات: {summary.get('cases')} | الدقة: {summary.get('accuracy')} | استدعاء النموذج: {summary.get('llm_call_rate')} | زمن: {summary.get('latency_ms_avg')}ms | ثبات: {summary.get('agreement_avg', 1.0)} | غير ثابت: {summary.get('unstable_cases', 0)} | تكرار: {repeats} | موديل: {pin_model or 'افتراضي'}",
        "",
        "| id | سؤال | متوقع | فعلي | صح؟ | مصدر |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        mark = "✓" if r.get("correct") else "✗"
        lines.append(f"| {r['id']} | {r['question'][:40]} | {r['expected']} | {r['predicted']} | {mark} | {r['source']} |")
    if summary.get("errors"):
        lines += ["", "## الأخطاء", ""]
        for e in summary["errors"]:
            lines.append(f"- {e['id']}: توقع `{e['expected']}` وأعطى `{e['predicted']}` — {e['question'][:60]}")
    md_path = out_dir / f"intent_{adapter_name}_{stamp}.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": str(json_path), "md": str(md_path)}
