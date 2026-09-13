"use client";
import { Button } from "@/components/ui/button";

export function ClarificationChips({ question, options, onSelect }: { question: string; options: string[]; onSelect: (opt: string) => void }) {
  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 my-2 dark:border-amber-800 dark:bg-amber-950/30">
      <p className="text-sm font-medium mb-3">🤔 {question}</p>
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => (
          <Button key={opt} variant="outline" size="sm" onClick={() => onSelect(opt)} className="rounded-full">
            {opt}
          </Button>
        ))}
      </div>
    </div>
  );
}
