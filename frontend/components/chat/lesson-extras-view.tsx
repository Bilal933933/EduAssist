"use client";

import { Flashcard, QuizQuestion } from "@/lib/types";

// وظيفة واحدة: عرض نتائج الإضافات (بطاقات/اختبار) — بدون جلب.
export function LessonExtrasView({
  cards,
  quiz,
}: {
  cards: Flashcard[] | null;
  quiz: QuizQuestion[] | null;
}) {
  if (!cards && !quiz) return null;

  return (
    <div className="mt-4 space-y-2">
      {cards && (
        <div className="space-y-2">
          {cards.map((c, i) => (
            <div key={i} className="rounded-xl border border-border p-3 text-[13px] leading-6">
              <p className="font-bold">س{i + 1}: {c.q}</p>
              <p className="text-foreground/80">ج: {c.a}</p>
            </div>
          ))}
        </div>
      )}
      {quiz && (
        <div className="space-y-2">
          {quiz.map((q, i) => (
            <div key={i} className="rounded-xl border border-border p-3 text-[13px] leading-6">
              <p className="font-bold">س{i + 1}: {q.q}</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 mt-2">
                {q.options.map((o: string, idx: number) => (
                  <span
                    key={idx}
                    className={idx === q.answer ? "font-bold text-emerald-700 dark:text-emerald-300" : "text-foreground/80"}
                  >
                    {idx + 1}. {o}
                  </span>
                ))}
              </div>
              {q.explain && <p className="text-xs text-muted-foreground mt-1.5">{q.explain}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
