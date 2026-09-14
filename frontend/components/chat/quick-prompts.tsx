"use client";

interface QuickPromptsProps {
  onSelectPrompt: (prompt: string) => void;
  disabled?: boolean;
}

const SUGGESTIONS = [
  "حضّر لي درس الفاعل — خطة شرح وسير حصة",
  "ما أفضل أسلوب لشرح الفاعل؟",
  "أنشئ اختباراً سريعاً عن الفاعل",
  "حضّر لي درس المبتدأ والخبر",
];

// وظيفة واحدة: شاشة البداية بأسلوب Gemini — تحية وحبوب اقتراحات فقط.
export function QuickPrompts({ onSelectPrompt, disabled }: QuickPromptsProps) {
  return (
    <div className="w-full max-w-2xl mx-auto my-10 px-2">
      <h2 className="text-xl sm:text-2xl font-bold text-foreground text-right leading-9">
        مرحباً، ماذا تحضّر اليوم؟
      </h2>
      <p className="text-sm text-muted-foreground mt-2 text-right leading-7">
        اكتب "حضر لي درس ..." أو اسأل عن أفضل أساليب الشرح
      </p>

      <div className="flex flex-col gap-2 mt-6">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            type="button"
            disabled={disabled}
            onClick={() => onSelectPrompt(s)}
            className="text-right text-[13px] px-4 py-2.5 rounded-2xl border border-border text-foreground/80 hover:border-foreground/40 hover:text-foreground hover:bg-muted/50 transition-colors disabled:opacity-50"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
