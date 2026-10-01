"use client";

import { Button } from "@/components/ui/button";

// تلميح غير حاجب تحت الإجابة العامة: شارة + سؤال الصف + أزرار صفوف.
// labels تطابق clarifier.GRADE_PATTERNS في الباك ليعمل التضييق عبر السياق.
const DEFAULT_GRADES = [
  "الصف الأول الابتدائي",
  "الصف الرابع الابتدائي",
  "الصف الخامس الابتدائي",
  "الصف السادس الابتدائي",
  "الصف الأول الإعدادي",
  "الصف الثاني الإعدادي",
  "الصف الثالث الإعدادي",
  "الصف الأول الثانوي",
  "الصف الثاني الثانوي",
  "الصف الثالث الثانوي",
];

export function ClarificationChips({ question, options, onSelect }: { question: string; options: string[]; onSelect: (opt: string) => void }) {
  const chips = options.length > 0 ? options : DEFAULT_GRADES;
  return (
    <div className="my-3 pr-9" dir="rtl">
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center rounded-full bg-muted px-2.5 py-0.5 text-[11px] font-bold text-muted-foreground">
          إجابة عامة
        </span>
        <p className="text-sm text-foreground">{question}</p>
      </div>
      <div className="flex flex-wrap gap-1.5 mt-2">
        {chips.map((opt) => (
          <Button key={opt} variant="outline" size="sm" onClick={() => onSelect(opt)} className="rounded-full text-xs">
            {opt}
          </Button>
        ))}
      </div>
    </div>
  );
}
