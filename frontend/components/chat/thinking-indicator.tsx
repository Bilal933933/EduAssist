"use client";

import { Sparkles } from "lucide-react";

export function ThinkingIndicator({ message }: { message?: string }) {
  return (
    <div className="flex justify-end items-start gap-3 my-5">
      <div className="bg-card border border-border/80 rounded-2xl rounded-tl-none p-4 shadow-sm flex items-center gap-3 ring-1 ring-border/50 text-right will-change-transform" dir="rtl">
        <span className="text-xs text-muted-foreground font-medium">
          {message || "جاري استرجاع القواعد وتحليل الشواهد النحوية..."}
        </span>
        <div className="flex gap-1.5 items-center">
          <span className="size-2 rounded-full bg-primary animate-bounce [animation-delay:-0.3s] will-change-transform"></span>
          <span className="size-2 rounded-full bg-primary animate-bounce [animation-delay:-0.15s] will-change-transform"></span>
          <span className="size-2 rounded-full bg-primary animate-bounce will-change-transform"></span>
        </div>
      </div>
      <div className="size-9 rounded-full bg-gradient-to-tr from-primary to-emerald-700 text-white flex items-center justify-center shrink-0 mt-1 shadow-md">
        <Sparkles className="size-4 text-amber-300" />
      </div>
    </div>
  );
}
