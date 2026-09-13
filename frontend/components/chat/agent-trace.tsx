"use client";

import { Brain, ChevronDown, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { AgentTraceStep } from "@/lib/types";
import { summarizeSteps, toArabicStepLabel } from "@/lib/agent-labels";

interface AgentTraceProps {
  steps: AgentTraceStep[];
  isStreaming: boolean;
  durationMs?: number;
  className?: string;
}

// وظيفة واحدة: عرض خطوات الوكيل كنص خافت قابل للطي — بدون بطاقة.
function formatDuration(durationMs?: number): string | null {
  if (!durationMs || durationMs <= 0) return null;
  const s = Math.max(1, Math.round(durationMs / 1000));
  if (s === 1) return "فكر لمدة ثانية";
  if (s === 2) return "فكر لمدة ثانيتين";
  if (s <= 10) return `فكر لمدة ${s} ثوانٍ`;
  return `فكر لمدة ${s} ثانية`;
}

export function AgentTrace({ steps, isStreaming, durationMs, className }: AgentTraceProps) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(isStreaming);
  }, [isStreaming]);

  if (!steps || steps.length === 0) return null;

  const summary = formatDuration(durationMs);
  const count = steps.length;
  const keyPoints = summarizeSteps(steps.map((s) => s.label));

  return (
    <div dir="rtl" className={className ?? ""}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        {isStreaming ? (
          <Loader2 className="size-3.5 animate-spin" />
        ) : (
          <Brain className="size-3.5" />
        )}
        <span>
          {isStreaming
            ? "أبحث وأجهز إجابتك..."
            : summary
              ? `${summary} · كيف توصلت للإجابة؟ (${count})`
              : `كيف توصلت للإجابة؟ (${count})`}
        </span>
        <ChevronDown className={`size-3.5 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {!open && keyPoints.length > 3 && (
        <p className="mt-1.5 text-xs text-muted-foreground leading-6">
          {keyPoints.slice(0, 3).join(" • ")}
          <button type="button" onClick={() => setOpen(true)} className="mr-1 underline underline-offset-4 hover:text-foreground">
            عرض التفاصيل
          </button>
        </p>
      )}

      {open && (
        <ol className="mt-2 space-y-1 border-r-2 border-border pr-3 text-xs text-muted-foreground">
          {steps.map((step, i) => (
            <li key={i} className="leading-6">
              <span className="text-foreground/80">{toArabicStepLabel(step.label)}</span>
              {step.detail && <span className="block text-[11px]">{step.detail}</span>}
            </li>
          ))}
          {isStreaming && <li className="text-foreground/70">جارٍ المتابعة...</li>}
        </ol>
      )}
    </div>
  );
}
