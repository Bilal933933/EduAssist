import Link from "next/link";
import { aggregateSubjects, subjectIcon, UNCLASSIFIED } from "@/lib/subjects";
import { formatCount } from "@/lib/utils";
import type { SubjectCount } from "@/lib/types";

interface SubjectsGridProps {
  rows: SubjectCount[] | undefined;
  totalChunks: number;
  indexed: boolean | undefined;
}

// وظيفة واحدة: قسم المواد المفهرسة في الصفحة الرئيسية — تجميع + شبكة + حالة فارغة.
export function SubjectsGrid({ rows, totalChunks, indexed }: SubjectsGridProps) {
  const subjects = aggregateSubjects(rows)
    .filter((s) => s.subject !== UNCLASSIFIED)
    .slice(0, 6);

  return (
    <section className="container py-10">
      <div className="flex items-end justify-between mb-4">
        <h2 className="font-bold text-lg text-right">موادك المفهرسة</h2>
        {indexed && (
          <p className="text-xs text-muted-foreground">{formatCount(totalChunks)} مقتطف من مصادرك</p>
        )}
      </div>
      {subjects.length > 0 ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {subjects.map((s) => {
            const Icon = subjectIcon(s.subject);
            return (
              <Link
                key={s.subject}
                href={`/subjects/${encodeURIComponent(s.subject)}`}
                className="border border-border rounded-2xl p-5 bg-card hover:shadow-md transition-shadow flex items-center gap-3"
              >
                <div className="size-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                  <Icon className="size-5" />
                </div>
                <div className="min-w-0">
                  <p className="font-bold text-sm truncate">{s.subject}</p>
                  <p className="text-xs text-muted-foreground">{formatCount(s.chunks)} مقتطف مفهرس</p>
                </div>
              </Link>
            );
          })}
        </div>
      ) : (
        <div className="border border-border rounded-2xl p-6 bg-card text-center text-sm text-muted-foreground">
          لا توجد مواد مفهرسة بعد — أضف مصادرك وشغّل الفهرسة لتظهر هنا.
        </div>
      )}
    </section>
  );
}
