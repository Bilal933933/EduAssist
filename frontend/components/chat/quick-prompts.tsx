"use client";

import { Sparkles, FileText, Zap, ClipboardCheck, BookOpen, MessagesSquare, BarChart3, Flame } from "lucide-react";

interface QuickPromptsProps {
  onSelectPrompt: (prompt: string) => void;
  disabled?: boolean;
}

const SUGGESTIONS = [
  {
    title: "ورقة عمل جاهزة",
    description: "أنشئ ورقة عمل لدرس الفاعل - الصف الخامس: مثال محلول + تدرج + نموذج إجابة",
    icon: FileText,
    tag: "ورقة عمل",
  },
  {
    title: "تدريبات ذكية",
    description: "أنشئ تدريبات موجهة لدرس الفاعل - الصف الخامس مع مراجعة متباعدة وتمييز المتشابه",
    icon: Zap,
    tag: "تدريبات",
  },
  {
    title: "اختبار سريع",
    description: "أنشئ اختباراً سريعاً لدرس الفاعل - الصف الخامس مع كشف الأخطاء وتفسير النتائج",
    icon: ClipboardCheck,
    tag: "اختبار",
  },
  {
    title: "قراءة وفهم",
    description: "أنشئ مادة قراءة وفهم لدرس الفاعل - الصف الخامس: نص مناسب + استدلال من النص",
    icon: BookOpen,
    tag: "قراءة",
  },
  {
    title: "مناقشة وتفكير",
    description: "أنشئ أسئلة مناقشة وتفكير عميق لدرس الفاعل - الصف الخامس مع أسئلة متابعة",
    icon: MessagesSquare,
    tag: "مناقشة",
  },
  {
    title: "وسيلة بصرية",
    description: "أنشئ وسيلة بصرية لدرس الفاعل - الصف الخامس: خريطة مفاهيم أو جدول مقارنة جاهز للطباعة",
    icon: BarChart3,
    tag: "وسيلة بصرية",
  },
  {
    title: "مراجعة شاملة",
    description: "أنشئ حزمة مراجعة شاملة لوحدة الجملة الفعلية - الصف الخامس مع بطاقات ونموذج إجابة",
    icon: Flame,
    tag: "مراجعة",
  },
];

export function QuickPrompts({ onSelectPrompt, disabled }: QuickPromptsProps) {
  return (
    <div className="w-full max-w-3xl mx-auto my-6 px-2 animate-in fade-in-50 duration-500">
      <div className="text-center mb-8 space-y-2.5">
        <div className="inline-flex items-center gap-2 bg-amber-500/10 text-amber-800 dark:text-amber-300 px-3.5 py-1 rounded-full text-xs font-bold border border-amber-500/25 shadow-2xs">
          <Sparkles className="size-3.5 text-amber-600 dark:text-amber-400" />
          <span>مساعد المدرس الذكي</span>
        </div>
        <h2 className="text-2xl sm:text-3xl font-extrabold text-foreground tracking-tight">
          ماذا تحضر اليوم؟
        </h2>
        <p className="text-sm text-muted-foreground max-w-lg mx-auto leading-relaxed">
          اكتب "حضر لي درس ..." أو اسأل عن أفضل أساليب الشرح:
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
        {SUGGESTIONS.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              type="button"
              disabled={disabled}
              onClick={() => onSelectPrompt(item.description)}
              className="text-right p-4 rounded-2xl border border-border/90 bg-card hover:bg-secondary/70 hover:border-primary/40 transition-all text-card-foreground flex items-start gap-3.5 group shadow-2xs hover:shadow-md active:scale-[0.99] disabled:opacity-50 cursor-pointer"
            >
              <div className="p-2.5 rounded-xl bg-primary/10 text-primary shrink-0 mt-0.5 group-hover:bg-primary group-hover:text-white transition-colors shadow-xs">
                <Icon className="size-5" />
              </div>
              <div className="space-y-1.5 overflow-hidden flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-foreground group-hover:text-primary transition-colors">
                    {item.title}
                  </span>
                  <span className="text-[10px] font-bold text-amber-800 dark:text-amber-300 bg-amber-500/10 px-2 py-0.5 rounded-md border border-amber-500/20">
                    {item.tag}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed group-hover:text-foreground/90 line-clamp-2 transition-colors">
                  {item.description}
                </p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
