"use client";

import { useEffect, useState } from "react";
import { toArabicStepLabel } from "@/lib/agent-labels";

// وظيفة واحدة: مؤشر انتظار نحيف بأسلوب Gemini — بدون بطاقة أو أفاتار.
export function ThinkingIndicator({ message }: { message?: string }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    setElapsed(0);
    const t = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="flex items-center gap-2 my-4 pr-9" dir="rtl" role="status" aria-live="polite">
      <div className="flex gap-1 items-center shrink-0" aria-hidden="true">
        <span className="size-1.5 rounded-full bg-foreground/50 animate-bounce [animation-delay:-0.3s]" />
        <span className="size-1.5 rounded-full bg-foreground/50 animate-bounce [animation-delay:-0.15s]" />
        <span className="size-1.5 rounded-full bg-foreground/50 animate-bounce" />
      </div>
      <p className="text-sm text-muted-foreground">
        {toArabicStepLabel(message || "") || "أبحث في مصادرك وأجهز الإجابة..."}
        <span className="tabular-nums"> · {elapsed} ث</span>
      </p>
    </div>
  );
}
