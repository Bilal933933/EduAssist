"""واجهة الهارنس — أمر واحد للمقارنة العادلة."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BACKEND = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND))
HARNESS = Path(__file__).resolve().parent
RESULTS = HARNESS / "results"


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=BACKEND.parent, text=True).strip()
    except Exception:
        return "unknown"


def load_cases(path: Path) -> list:
    return json.loads(path.read_text(encoding="utf-8"))["cases"]


def main() -> int:
    ap = argparse.ArgumentParser(description="هارنس النية — مقارنة rule/hybrid")
    ap.add_argument("--adapter", default="all", choices=["rule", "hybrid", "all"])
    ap.add_argument("--dataset", default=str(HARNESS / "datasets" / "intent_cases.json"))
    ap.add_argument("--repeats", type=int, default=3, help="عدد تكرارات كل حالة لكشف العشوائية (1 للسلوك القديم)")
    ap.add_argument("--pin-model", default="", help="تثبيت الموديل لمنع fallback (مثال: gemini-3.5-flash)")
    args = ap.parse_args()

    from eval.harness.adapters import hybrid_classify, rule_classify
    from eval.harness.metrics import summarize
    from eval.harness.report import save
    from eval.harness.runner import run_all

    cases = load_cases(Path(args.dataset))
    commit = git_commit()
    todo = ["rule", "hybrid"] if args.adapter == "all" else [args.adapter]
    for name in todo:
        fn = rule_classify if name == "rule" else hybrid_classify
        # معزول بلا شبكة: client=None → الهجين يسقط للقاعدة حتمياً (تكرار واحد يكفي)
        results = run_all(fn, cases, client=None, repeats=args.repeats, pin_model=args.pin_model or None)
        summary = summarize(results)
        paths = save(name, results, summary, RESULTS, commit, repeats=args.repeats, pin_model=args.pin_model or None)
        print(f"[{name}] cases={summary['cases']} accuracy={summary['accuracy']} llm_rate={summary['llm_call_rate']} avg={summary['latency_ms_avg']}ms agreement={summary.get('agreement_avg', 1.0)} unstable={summary.get('unstable_cases', 0)}")
        print(f"saved: {paths['json']}")
        if summary.get("errors"):
            for e in summary["errors"][:8]:
                print(f"  ✗ {e['id']}: expected={e['expected']} got={e['predicted']} — {e['question'][:50]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
