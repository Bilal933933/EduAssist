"use client";

import { Button } from "@/components/ui/button";

// وظيفة واحدة: رقائق التوضيح بأسلوب خافت — بدون بطاقة ملونة.
export function ClarificationChips({ question, options, onSelect }: { question: string; options: string[]; onSelect: (opt: string) => void }) {
  return (
    <div className="my-3 pr-9" dir="rtl">
      <p className="text-sm text-foreground">{question}</p>
      <div className="flex flex-wrap gap-1.5 mt-2">
        {options.map((opt) => (
          <Button key={opt} variant="outline" size="sm" onClick={() => onSelect(opt)} className="rounded-full text-xs">
            {opt}
          </Button>
        ))}
      </div>
    </div>
  );
}
