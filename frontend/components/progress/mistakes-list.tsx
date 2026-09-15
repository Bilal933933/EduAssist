import { AlertTriangle } from "lucide-react";
import { formatCount } from "@/lib/utils";
import type { TeacherProfile } from "@/lib/types";

type Mistake = TeacherProfile["common_mistakes"][number];

// وظيفة واحدة: قائمة الأخطاء الشائعة المسجلة.
export function MistakesList({ mistakes }: { mistakes: Mistake[] }) {
  return (
    <div className="border border-amber-500/20 bg-amber-500/5 rounded-2xl p-5">
      <p className="font-bold text-sm flex items-center gap-2">
        <AlertTriangle className="size-4 text-amber-600" /> أخطاء شائعة مسجلة
      </p>
      {mistakes.length > 0 ? (
        <ul className="mt-3 space-y-2 text-sm">
          {mistakes.slice(0, 6).map((m) => (
            <li key={m.id} className="flex items-start justify-between gap-3">
              <span>{m.mistake}</span>
              <span className="text-xs text-muted-foreground shrink-0">{formatCount(m.count)}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-muted-foreground mt-3">لا أخطاء مسجلة — تظهر عند رصد أخطاء متكررة في شرحك.</p>
      )}
    </div>
  );
}
