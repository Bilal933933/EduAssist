"use client";

import Link from "next/link";
import { Spinner } from "@/components/ui/spinner";
import { useStats } from "@/lib/queries";
import { aggregateSubjects, subjectIcon, UNCLASSIFIED } from "@/lib/subjects";
import { formatCount } from "@/lib/utils";

export default function SubjectsPage() {
  const { data: stats, isPending, isError } = useStats();
  const subjects = aggregateSubjects(stats?.by_subject);
  const maxChunks = subjects.reduce((max, s) => Math.max(max, s.chunks), 1);

  return (
    <div className="container py-6 space-y-6">
      <div>
        <h1 className="text-xl font-extrabold">موادك الدراسية</h1>
        <p className="text-sm text-muted-foreground mt-1">
          المواد المفهرسة من مصادرك الخاصة — اختر مادة لاستعراض مراحلها
        </p>
      </div>

      {isPending ? (
        <div className="flex justify-center py-10">
          <Spinner className="size-6" />
        </div>
      ) : isError ? (
        <div className="border border-destructive/30 bg-destructive/5 rounded-2xl p-6 text-center text-sm text-muted-foreground">
          تعذر جلب قائمة المواد — حاول تحديث الصفحة.
        </div>
      ) : subjects.length === 0 ? (
        <div className="border border-border rounded-2xl p-6 bg-card text-center text-sm text-muted-foreground">
          لا توجد مواد مفهرسة بعد — أضف محتوى إلى مجلد content ثم شغّل الفهرسة.
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {subjects.map((s) => {
            const Icon = subjectIcon(s.subject);
            const stagesCount = s.stages.length;
            const unclassified = s.subject === UNCLASSIFIED;
            return (
              <Link
                key={s.subject}
                href={`/subjects/${encodeURIComponent(s.subject)}`}
                className="border border-border rounded-2xl p-5 bg-card hover:shadow-md hover:border-primary/30 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div className="size-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                    <Icon className="size-5" />
                  </div>
                  <div className="min-w-0">
                    <p className="font-bold text-sm truncate">{s.subject}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatCount(s.chunks)} مقتطف{stagesCount > 1 ? ` • ${formatCount(stagesCount)} مراحل` : ""}
                    </p>
                  </div>
                </div>
                {!unclassified && (
                  <div className="mt-4 h-1.5 bg-secondary rounded-full overflow-hidden">
                    <div className="h-full bg-primary rounded-full" style={{ width: `${Math.round((s.chunks / maxChunks) * 100)}%` }} />
                  </div>
                )}
                <p className="text-xs text-muted-foreground mt-2">
                  {s.stages.map((st) => st.stage || "بدون مرحلة").join(" • ")}
                </p>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
