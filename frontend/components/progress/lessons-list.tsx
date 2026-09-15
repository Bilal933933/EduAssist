import { Clock } from "lucide-react";
import { cleanGradeLabel } from "@/lib/memory";
import { formatArabicDate } from "@/lib/utils";
import type { TeacherLessonEvent } from "@/lib/types";

// وظيفة واحدة: قائمة آخر الدروس المحضّرة.
export function LessonsList({ lessons }: { lessons: TeacherLessonEvent[] }) {
  return (
    <div className="border border-border rounded-2xl p-5 bg-card">
      <p className="font-bold text-sm flex items-center gap-2">
        <Clock className="size-4 text-primary" /> آخر دروس حضّرتها
      </p>
      {lessons.length > 0 ? (
        <ul className="mt-4 space-y-3">
          {lessons.slice(0, 8).map((l, i) => {
            const grade = cleanGradeLabel(l.grade);
            return (
              <li key={`${l.topic}-${i}`} className="flex items-start justify-between gap-3 text-sm">
                <span className="font-medium leading-6">{l.topic}</span>
                <span className="text-xs text-muted-foreground shrink-0 text-left">
                  {[grade, formatArabicDate(l.at)].filter(Boolean).join(" • ")}
                </span>
              </li>
            );
          })}
        </ul>
      ) : (
        <p className="text-sm text-muted-foreground mt-3">
          لا دروس محضّرة بعد — اطلب من المساعد تحضير درس وسيظهر هنا.
        </p>
      )}
    </div>
  );
}
