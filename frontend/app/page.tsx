import Link from "next/link";
import { LandingHero } from "@/components/edu/landing-hero";
import { Button } from "@/components/ui/button";
import { BookOpen, Layers, GraduationCap } from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-dvh bg-background">
      <header className="sticky top-0 z-30 bg-background/80 backdrop-blur border-b border-border">
        <div className="container flex h-14 items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="size-8 rounded-xl bg-primary text-primary-foreground flex items-center justify-center font-bold">م</div>
            <span className="font-bold">EduAssist</span>
            <span className="text-xs text-muted-foreground hidden sm:inline">مساعدي</span>
          </div>
          <div className="flex items-center gap-2">
            <Button asChild variant="ghost" size="sm"><Link href="/dashboard">لوحة التحكم</Link></Button>
            <Button asChild size="sm" className="rounded-full"><Link href="/assistant">جرّب المساعد</Link></Button>
          </div>
        </div>
      </header>
      <LandingHero />
      <section className="container py-10">
        <h2 className="font-bold text-lg mb-4 text-right">موادك الدراسية</h2>
        <div className="grid sm:grid-cols-3 gap-4">
          {[
            { name: "اللغة العربية", progress: "8/14 درس", icon: BookOpen },
            { name: "الرياضيات", progress: "6/18 درس", icon: Layers },
            { name: "العلوم", progress: "4/12 درس", icon: GraduationCap },
          ].map((s) => (
            <Link key={s.name} href="/subjects" className="border border-border rounded-2xl p-5 bg-card hover:shadow-md transition-shadow flex items-center gap-3">
              <div className="size-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center"><s.icon className="size-5" /></div>
              <div><p className="font-bold text-sm">{s.name}</p><p className="text-xs text-muted-foreground">{s.progress}</p></div>
            </Link>
          ))}
        </div>
      </section>
      <footer className="border-t border-border py-6 text-center text-xs text-muted-foreground">EduAssist — مساعدك الذكي للتعلّم • Learn smarter. Understand better.</footer>
    </div>
  );
}
