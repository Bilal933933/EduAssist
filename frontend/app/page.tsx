import Link from "next/link";
import { LandingHero } from "@/components/edu/landing-hero";
import { Button } from "@/components/ui/button";
import { API_BASE_URL } from "@/lib/config";
import { StatsResponse } from "@/lib/types";
import { aggregateSubjects, subjectIcon, UNCLASSIFIED } from "@/lib/subjects";
import { formatCount } from "@/lib/utils";

async function getStats(): Promise<StatsResponse | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/stats`, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export default async function HomePage() {
  const stats = await getStats();
  const subjects = aggregateSubjects(stats?.by_subject)
    .filter((s) => s.subject !== UNCLASSIFIED)
    .slice(0, 6);

  return (
    <div className="min-h-dvh bg-background">
      <header className="sticky top-0 z-30 bg-background/80 backdrop-blur border-b border-border">
        <div className="container flex h-14 items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="size-8 rounded-xl bg-primary text-primary-foreground flex items-center justify-center font-bold">م</div>
            <span className="font-bold">EduAssist</span>
            <span className="text-xs text-muted-foreground hidden sm:inline">مساعد المدرس</span>
          </div>
          <div className="flex items-center gap-2">
            <Button asChild variant="ghost" size="sm"><Link href="/dashboard">لوحة التحكم</Link></Button>
            <Button asChild size="sm" className="rounded-full"><Link href="/assistant">جرّب المساعد</Link></Button>
          </div>
        </div>
      </header>
      <LandingHero />
      <section className="container py-10">
        <div className="flex items-end justify-between mb-4">
          <h2 className="font-bold text-lg text-right">موادك المفهرسة</h2>
          {stats?.indexed && (
            <p className="text-xs text-muted-foreground">{formatCount(stats.total_chunks)} مقتطف من مصادرك</p>
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
      <footer className="border-t border-border py-6 text-center text-xs text-muted-foreground">
        EduAssist — مساعد المدرس الذكي
      </footer>
    </div>
  );
}
