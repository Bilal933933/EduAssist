"use client";

import { AlertTriangle, CheckCircle2, Clock, TrendingUp } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";
import { useMemory, useStats, useThreads } from "@/lib/queries";
import { cleanGradeLabel, mergeTopics } from "@/lib/memory";
import { formatArabicDate, formatCount } from "@/lib/utils";

export default function ProgressPage() {
  const { data: stats } = useStats();
  const { data: threads = [], isLoading: threadsLoading } = useThreads(true);
  const { data: memory, isLoading: memoryLoading } = useMemory(true);

  const profile = memory?.profile;
  const loading = threadsLoading || memoryLoading;

  const messageTotal = threads.reduce((sum, t) => sum + (t.message_count || 0), 0);
  const topics = mergeTopics(profile?.frequent_topics);
  const maxCount = topics.reduce((max, t) => Math.max(max, t.count), 1);
  const lessons = profile?.recent_lessons ?? [];
  const mistakes = profile?.common_mistakes ?? [];
  const grades = (profile?.preferred_grades ?? []).map(cleanGradeLabel).filter((g): g is string => !!g);

  return (
    <div className="container py-6 space-y-6">
      <div>
        <h1 className="text-xl font-extrabold">سجلي كمدرس</h1>
        <p className="text-sm text-muted-foreground mt-1">
          ملخص حقيقي من محادثاتك ومصادرك المفهرسة — يتحدث تلقائياً مع كل استخدام
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center py-10">
          <Spinner className="size-6" />
        </div>
      ) : (
        <>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="border border-border rounded-2xl p-5 bg-card text-center">
              <p className="text-3xl font-extrabold">{formatCount(threads.length)}</p>
              <p className="text-xs text-muted-foreground mt-1">محادثة محفوظة</p>
              <p className="text-[11px] text-muted-foreground mt-2">
                {messageTotal > 0 ? `بإجمالي ${formatCount(messageTotal)} رسالة` : "ابدأ أول محادثة من المساعد"}
              </p>
            </div>
            <div className="border border-border rounded-2xl p-5 bg-card text-center">
              <p className="text-3xl font-extrabold">{formatCount(profile?.interaction_count ?? 0)}</p>
              <p className="text-xs text-muted-foreground mt-1">تفاعل مع مساعدك</p>
              <p className="text-[11px] text-muted-foreground mt-2">
                {formatCount(stats?.total_chunks ?? 0)} مقتطف مفهرس من مصادرك
              </p>
            </div>
            <div className="border border-border rounded-2xl p-5 bg-card text-center">
              <p className="text-3xl font-extrabold">{formatCount(topics.length)}</p>
              <p className="text-xs text-muted-foreground mt-1">موضوعاً في سجلك</p>
              {grades.length > 0 && (
                <p className="text-[11px] text-muted-foreground mt-2 truncate">{grades.join(" • ")}</p>
              )}
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="border border-border rounded-2xl p-5 bg-card">
              <p className="font-bold text-sm flex items-center gap-2">
                <TrendingUp className="size-4 text-primary" /> مواضيعك الأكثر تكراراً
              </p>
              {topics.length > 0 ? (
                <ul className="mt-4 space-y-3">
                  {topics.slice(0, 8).map((t) => (
                    <li key={t.topic}>
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium truncate">{t.topic}</span>
                        <span className="text-xs text-muted-foreground tabular-nums">{formatCount(t.count)}</span>
                      </div>
                      <div className="h-1.5 bg-secondary rounded-full mt-1.5 overflow-hidden">
                        <div className="h-full bg-primary rounded-full" style={{ width: `${Math.round((t.count / maxCount) * 100)}%` }} />
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground mt-3">
                  لا مواضيع مسجلة بعد — ستُبنى تلقائياً من أسئلتك.
                </p>
              )}
            </div>

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
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="border border-border rounded-2xl p-5 bg-card">
              <p className="font-bold text-sm flex items-center gap-2">
                <CheckCircle2 className="size-4 text-emerald-600" /> مواضيع تتكرر في سجلك
              </p>
              {topics.filter((t) => t.count >= 2).length > 0 ? (
                <div className="flex flex-wrap gap-2 mt-3">
                  {topics.filter((t) => t.count >= 2).slice(0, 6).map((t) => (
                    <span key={t.topic} className="text-xs bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 px-2.5 py-1 rounded-full">
                      {t.topic}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground mt-3">ستظهر هنا المواضيع التي تعود إليها أكثر من مرة.</p>
              )}
            </div>
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
          </div>

          {(profile?.summary || profile?.class_context) && (
            <div className="border border-border rounded-2xl p-5 bg-card">
              <p className="font-bold text-sm">ملخص مساعدك عنك</p>
              {profile?.summary && <p className="text-sm leading-7 mt-2 text-foreground/90">{profile.summary}</p>}
              {profile?.class_context && <p className="text-sm leading-7 mt-2 text-muted-foreground">{profile.class_context}</p>}
            </div>
          )}
        </>
      )}
    </div>
  );
}
