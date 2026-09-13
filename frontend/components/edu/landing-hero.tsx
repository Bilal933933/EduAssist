"use client";
import Link from "next/link";
import { Sparkles, BookOpen, HelpCircle, BarChart3, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

export function LandingHero() {
  return (
    <section className="container py-10 sm:py-16">
      <div className="grid lg:grid-cols-2 gap-10 items-center">
        <div className="space-y-6 text-right">
          <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-bold border border-primary/20">
            <Sparkles className="size-3.5" />
            EduAssist — مساعدي الذكي للتعلّم
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-[42px] font-extrabold leading-tight tracking-tight">
            تعلّم بطريقة أذكى.
            <span className="text-primary block mt-2">مساعد يفهم دروسك.</span>
          </h1>
          <p className="text-muted-foreground leading-relaxed max-w-xl">
            ليس مجرد chatbot للنحو. EduAssist يعرف منهجك — الصف، المادة، الوحدة والدرس — يشرح لك، يحل معك، ويختبر فهمك. من التحضير إلى المراجعة.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button asChild size="lg" className="rounded-full px-7">
              <Link href="/dashboard">ابدأ التعلم مجاناً <ArrowLeft className="size-4 mr-2" /></Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="rounded-full">
              <Link href="/assistant">جرّب المساعد</Link>
            </Button>
          </div>
          <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2">
            <span className="flex items-center gap-1"><span className="size-2 rounded-full bg-emerald-500" /> يعمل مع منهجك</span>
            <span>• لا حفظ وتلقين</span>
            <span>• فهم حقيقي</span>
          </div>
        </div>
        <div className="relative">
          <div className="bg-card border border-border rounded-[28px] shadow-xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold">👋 مرحباً يا أحمد</span>
              <span className="text-xs bg-secondary px-2 py-1 rounded-full">الصف الثالث الإعدادي</span>
            </div>
            <p className="text-sm font-medium">ماذا تريد أن تتعلم اليوم؟</p>
            <div className="grid grid-cols-2 gap-3">
              {[
                { icon: BookOpen, label: "شرح درس", desc: "بطريقة مبسطة" },
                { icon: HelpCircle, label: "حل سؤال", desc: "نحلّه معاً" },
                { icon: Sparkles, label: "اختبر نفسك", desc: "اختبار قصير" },
                { icon: BarChart3, label: "راجع معي", desc: "قبل الامتحان" },
              ].map((c) => (
                <div key={c.label} className="border border-border rounded-2xl p-4 flex flex-col gap-1 hover:bg-secondary/50 transition-colors">
                  <c.icon className="size-5 text-primary" />
                  <span className="font-bold text-sm">{c.label}</span>
                  <span className="text-xs text-muted-foreground">{c.desc}</span>
                </div>
              ))}
            </div>
            <div className="bg-secondary/60 rounded-xl p-3 text-xs leading-relaxed">
              <span className="font-bold">مُعين:</span> خلينا نبسط "كان وأخواتها" — تدخل على الجملة الاسمية فتبقي المبتدأ مرفوعاً وتنصب الخبر. مثال: الجوُّ جميلٌ → كان الجوُّ جميلاً. ماذا حدث للخبر؟
            </div>
          </div>
          <div className="absolute -bottom-4 -left-4 bg-primary text-primary-foreground text-xs px-3 py-2 rounded-full shadow-lg hidden sm:block">يفهم منهجك • يتذكر مستواك</div>
        </div>
      </div>
    </section>
  );
}
