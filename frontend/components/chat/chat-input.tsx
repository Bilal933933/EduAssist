"use client";

import { useState, KeyboardEvent } from "react";
import { ArrowUp } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

const QUICK_CHIPS = ["ورقة عمل", "خطة درس", "اختبار قصير", "أنشطة تفاعلية"];

// وظيفة واحدة: حبة إدخال بأسلوب Gemini — بدون ظل ثقيل.
export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [text, setText] = useState("");

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (!text.trim() || isLoading) return;
    onSend(text.trim());
    setText("");
  };

  return (
    <div className="w-full max-w-2xl mx-auto px-1 sm:px-2 pt-1">
      <div
        className="rounded-[1.75rem] border border-border bg-background shadow-float focus-within:border-foreground/30 transition-colors px-3.5 pt-2 pb-1.5"
        role="form"
        aria-label="إرسال سؤال للمدرس"
      >
        <label htmlFor="chat-input" className="sr-only">سؤال للمدرس</label>
        <textarea
          id="chat-input"
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="اسأل عن أي درس..."
          disabled={isLoading}
          aria-label="حقل إدخال السؤال"
          className="w-full resize-none bg-transparent text-sm outline-none placeholder:text-muted-foreground leading-7 text-foreground field-sizing-content max-h-[160px] overflow-y-auto"
        />
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-muted-foreground">يبحث في مصادرك أولاً ثم يجيب</span>
          <Button
            type="button"
            size="icon"
            onClick={handleSubmit}
            disabled={!text.trim() || isLoading}
            aria-label="إرسال السؤال"
            className="size-8 rounded-full shrink-0"
          >
            <ArrowUp className="size-3.5" aria-hidden="true" />
          </Button>
        </div>
      </div>
      <div className="flex gap-1.5 mt-1.5 justify-start sm:justify-center overflow-x-auto scrollbar-hide pb-0.5" aria-label="اقتراحات سريعة">
        {QUICK_CHIPS.map((chip) => (
          <button
            key={chip}
            type="button"
            disabled={isLoading}
            onClick={() => setText((prev) => (prev.trim() ? `${prev.trim()} ` : "") + chip + " ")}
            className="text-[10px] whitespace-nowrap px-2.5 py-1 rounded-full border border-border text-muted-foreground hover:text-foreground hover:border-foreground/40 transition-colors disabled:opacity-50 shrink-0"
          >
            {chip}
          </button>
        ))}
      </div>
    </div>
  );
}
