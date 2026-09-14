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
            EduAssist — مساعد المدرس الذكي
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-[42px] font-extrabold leading-tight tracking-tight">
            حضّر دروسك بذكاء.
            <span className="text-primary block mt-2">مساعد يقرأ مصادرك.</span>
          </h1>
          <p className="text-muted-foreground leading-relaxed max-w-xl">
            ليس مجرد chatbot. EduAssist يعرف محتواك — المادة، المرحلة، الدرس — ويبني لك خطة شرح وسير حصة
            وتدريبات، من مصادرك الخاصة فقط. من التحضير إلى النقاش التربوي.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button asChild size="lg" className="rounded-full px-7">
              <Link href="/dashboard">ابدأ التحضير <ArrowLeft className="size-4 mr-2" /></Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="rounded-full">
              <Link href="/assistant">جرّب المساعد</Link>
            </Button>
          </div>
          <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2">
            <span className="flex items-center gap-1"><span className="size-2 rounded-full bg-emerald-500" /> من مصادرك الخاصة فقط</span>
            <span>• عربية بالكامل</span>
            <span>• يتذكر سياقك</span>
          </div>
        </div>
        <div className="relative">
          <div className="bg-card border border-border rounded-[28px] shadow-xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold">حضّر لي درس الفاعل</span>
              <span className="text-xs bg-secondary px-2 py-1 rounded-full">اللغة العربية</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {[
                { icon: BookOpen, label: "خطة شرح", desc: "أهداف وخطوات" },
                { icon: HelpCircle, label: "سير حصة", desc: "تهيئة وتقويم" },
                { icon: Sparkles, label: "تدريبات", desc: "أسئلة متدرجة" },
                { icon: BarChart3, label: "مصادر", desc: "مع كل مقطع" },
              ].map((c) => (
                <div key={c.label} className="border border-border rounded-2xl p-4 flex flex-col gap-1 hover:bg-secondary/50 transition-colors">
                  <c.icon className="size-5 text-primary" />
                  <span className="font-bold text-sm">{c.label}</span>
                  <span className="text-xs text-muted-foreground">{c.desc}</span>
                </div>
              ))}
            </div>
            <div className="bg-secondary/60 rounded-xl p-3 text-xs leading-relaxed">
              <span className="font-bold">المساعد:</span> الفاعل اسم مرفوع يدل على من قام بالفعل. خطة الحصة:
              تهيئة بأمثلة من درس سابق، ثم استخراج الفاعل من جمل المنهج، وتقويم ختامي بثلاثة أسئلة متدرجة.
            </div>
          </div>
          <div className="absolute -bottom-4 -left-4 bg-primary text-primary-foreground text-xs px-3 py-2 rounded-full shadow-lg hidden sm:block">يفهم مصادرك • يتذكر سياقك</div>
        </div>
      </div>
    </section>
  );
}
