import Link from "next/link";
import { LandingHero } from "@/components/edu/landing-hero";
import { SubjectsGrid } from "@/components/edu/subjects-grid";
import { Button } from "@/components/ui/button";
import { SERVER_API_BASE_URL } from "@/lib/config";
import { StatsResponse } from "@/lib/types";

async function getStats(): Promise<StatsResponse | null> {
  try {
    const res = await fetch(`${SERVER_API_BASE_URL}/api/stats`, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    const j = await res.json();
    return (j?.ok === true ? j.data : j) as StatsResponse;
  } catch {
    return null;
  }
}

export default async function HomePage() {
  const stats = await getStats();

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
      <SubjectsGrid
        rows={stats?.by_subject}
        totalChunks={stats?.total_chunks ?? 0}
        indexed={stats?.indexed}
      />
      <footer className="border-t border-border py-6 text-center text-xs text-muted-foreground">
        EduAssist — مساعد المدرس الذكي
      </footer>
    </div>
  );
}
