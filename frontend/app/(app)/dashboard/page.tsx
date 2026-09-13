import Link from "next/link";
import { BookOpen, HelpCircle, Sparkles, BarChart3, ArrowLeft, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  return (
    <div className="container py-6 space-y-6">
      <div className="bg-card border border-border rounded-2xl p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold">مساء الخير أستاذ أحمد 👋</h1>
          <p className="text-sm text-muted-foreground mt-1">جاهز لتحضير درس اليوم؟</p>
          <div className="mt-3 flex items-center gap-2 text-xs">
            <span className="bg-primary text-primary-foreground px-2 py-1 rounded-full font-bold">اللغة العربية — كان وأخواتها</span>
            <span className="text-muted-foreground">آخر خطة حضرتها</span>
          </div>
          <div className="mt-2 h-2 bg-secondary rounded-full overflow-hidden w-64">
            <div className="h-full bg-primary rounded-full" style={{ width: "57%" }} />
          </div>
          <p className="text-[11px] text-muted-foreground mt-1">حضّرت 8 / 14 درساً للثالث الإعدادي</p>
        </div>
        <Button asChild className="rounded-full"><Link href="/assistant">حضّر درساً جديداً <ArrowLeft className="size-4 mr-2" /></Link></Button>
      </div>

      <div>
        <h2 className="font-bold mb-3">ماذا تريد أن تحضّر؟</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            { label: "حضّر درس", desc: "خطة شرح + سير حصة كاملة من مصادرك", icon: BookOpen, href: "/assistant" },
            { label: "ناقش الأسلوب", desc: "اقتراح طرق تدريس مشوقة للدرس", icon: HelpCircle, href: "/assistant" },
            { label: "حاكِ الطلاب", desc: "درّب شرحك مع طلاب افتراضيين (قريباً)", icon: Sparkles, href: "/assistant" },
            { label: "سجلي", desc: "مراجعة خططك المحضرة وتغطية المنهج", icon: BarChart3, href: "/progress" },
          ].map((c) => (
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
          <p className="text-xs text-muted-foreground flex items-center gap-1"><Clock className="size-3" /> آخر تحضير</p>
          <p className="font-bold text-sm mt-2">كان وأخواتها — الثالث الإعدادي</p>
          <p className="text-xs text-muted-foreground">خطة + سير حصة + تدريبات — جاهزة للطباعة</p>
        </div>
        <div className="border border-border rounded-2xl p-4 bg-card">
          <p className="text-xs text-muted-foreground">تغطية المنهج</p>
          <p className="text-2xl font-extrabold mt-1">8 / 14</p>
          <p className="text-xs text-muted-foreground">خطة محضرة • من مصادرك الخاصة</p>
        </div>
        <div className="border border-primary/30 bg-primary/5 rounded-2xl p-4">
          <p className="font-bold text-sm">ماذا تحضّر الآن؟</p>
          <Link href="/assistant" className="mt-3 inline-flex w-full bg-primary text-primary-foreground rounded-full py-2 text-sm font-bold justify-center">اسأل مساعدك</Link>
          <p className="text-[11px] text-muted-foreground text-center mt-2">اللغة العربية • الثالث الإعدادي</p>
        </div>
      </div>
    </div>
  );
}
