"use client";

import Link from "next/link";
import { ArrowLeft, BarChart3, BookOpen, HelpCircle, MessageSquare, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { useMemory, useStats, useStoredUser, useThreads } from "@/lib/queries";
import { mergeTopics } from "@/lib/memory";
import { aggregateSubjects, UNCLASSIFIED } from "@/lib/subjects";
import { formatArabicDate, formatCount } from "@/lib/utils";

export default function DashboardPage() {
  const user = useStoredUser();
  const { data: stats } = useStats();
  const { data: threads = [], isLoading: threadsLoading } = useThreads(true);
  const { data: memory } = useMemory(true);

  const subjects = aggregateSubjects(stats?.by_subject).filter((s) => s.subject !== UNCLASSIFIED);
  const topics = mergeTopics(memory?.profile.frequent_topics).slice(0, 3);
  const lastThread = threads[0] ?? null;

  const greeting = user?.name?.trim() ? `مرحباً ${user.name.trim()}` : "مرحباً بك";
  const chunks = stats?.total_chunks ?? 0;

  const actions = [
    { label: "حضّر درساً", desc: "خطة شرح + سير حصة من مصادرك", icon: BookOpen, href: "/assistant" },
    { label: "ناقش الأسلوب", desc: "اقتراح طرائق تدريس من مصادر تربوية", icon: HelpCircle, href: "/assistant" },
    { label: "اختبر وذاكر", desc: "بطاقات مراجعة واختبارات سريعة", icon: Sparkles, href: "/assistant" },
    { label: "سجلي", desc: "محادثاتك ومواضيعك الأكثر تكراراً", icon: BarChart3, href: "/progress" },
  ];

  return (
    <div className="container py-6 space-y-6">
      <div className="bg-card border border-border rounded-2xl p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold">{greeting}</h1>
          <p className="text-sm text-muted-foreground mt-1">جاهز لتحضير درس اليوم؟</p>
          <p className="text-xs text-muted-foreground mt-3">
            {!stats
              ? "جارٍ قراءة مصادرك..."
              : stats.indexed
                ? `مصادرك مُفهرسة — ${formatCount(chunks)} مقتطف موزّعة على ${formatCount(subjects.length)} مواد`
                : "لا توجد مصادر مفهرسة بعد — أضف محتوى وشغّل الفهرسة"}
          </p>
        </div>
        <Button asChild className="rounded-full">
          <Link href="/assistant">
            حضّر درساً جديداً <ArrowLeft className="size-4 mr-2" />
          </Link>
        </Button>
      </div>

      <div>
        <h2 className="font-bold mb-3">ماذا تريد أن تحضّر؟</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {actions.map((c) => (
            <Link key={c.label} href={c.href} className="border border-border rounded-2xl p-4 bg-card hover:bg-secondary/50 transition-colors">
              <c.icon className="size-5 text-primary mb-2" />
              <p className="font-bold text-sm">{c.label}</p>
              <p className="text-xs text-muted-foreground leading-relaxed">{c.desc}</p>
            </Link>
          ))}
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="border border-border rounded-2xl p-4 bg-card">
          <p className="text-xs text-muted-foreground flex items-center gap-1">
            <MessageSquare className="size-3" /> آخر محادثة
          </p>
          {threadsLoading ? (
            <Spinner className="size-4 mt-3" />
          ) : lastThread ? (
            <>
              <p className="font-bold text-sm mt-2 leading-6">{lastThread.title}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {formatArabicDate(lastThread.updated_at)}
                {lastThread.message_count ? ` • ${formatCount(lastThread.message_count)} رسالة` : ""}
              </p>
            </>
          ) : (
            <p className="text-sm text-muted-foreground mt-2">لا محادثات بعد — ابدأ أول سؤال من المساعد.</p>
          )}
        </div>

        <div className="border border-border rounded-2xl p-4 bg-card">
          <p className="text-xs text-muted-foreground">مواضيعك الأكثر تكراراً</p>
          {topics.length > 0 ? (
            <ul className="mt-2 space-y-1.5">
              {topics.map((t) => (
                <li key={t.topic} className="flex items-center justify-between text-sm">
                  <span className="font-bold truncate">{t.topic}</span>
                  <span className="text-xs text-muted-foreground tabular-nums">{formatCount(t.count)} مرة</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted-foreground mt-2">ستظهر مواضيعك هنا بعد أول محادثات.</p>
          )}
        </div>

        <div className="border border-primary/30 bg-primary/5 rounded-2xl p-4">
          <p className="font-bold text-sm">ماذا تحضّر الآن؟</p>
          <Link href="/assistant" className="mt-3 inline-flex w-full bg-primary text-primary-foreground rounded-full py-2 text-sm font-bold justify-center">
            اسأل مساعدك
          </Link>
          <p className="text-[11px] text-muted-foreground text-center mt-2">
            {memory?.profile.interaction_count
              ? `${formatCount(memory.profile.interaction_count)} تفاعل مع مساعدك`
              : "مبني على مصادرك الخاصة"}
          </p>
        </div>
      </div>
    </div>
  );
}
