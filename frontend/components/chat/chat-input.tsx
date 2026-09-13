"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { Send, CornerDownLeft, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        180
      )}px`;
    }
  }, [text]);

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
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-4 sm:pb-5 pt-3">
      <div className="relative rounded-2xl border border-border/90 bg-card shadow-lg shadow-black/5 focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20 transition-all p-2" role="form" aria-label="إرسال سؤال للمدرس">
        <label htmlFor="chat-input" className="sr-only">سؤال للمدرس</label>
        <textarea
          id="chat-input"
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="اطرح سؤالك النحوي هنا... (مثال: ما إعراب 'إياك نعبد'؟)"
          disabled={isLoading}
          aria-label="حقل إدخال سؤال نحوي"
          aria-multiline="true"
          aria-disabled={isLoading}
          className="w-full resize-none bg-transparent px-3 py-2 text-sm sm:text-base outline-none placeholder:text-muted-foreground/70 leading-relaxed text-foreground"
        />

        <div className="flex items-center justify-between pt-2 px-2 border-t border-border/40">
          <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
            <Sparkles className="size-3 text-primary" />
            <span>مدعوم بـ Gemini 3.6 Flash & RAG</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden sm:inline text-[11px] text-muted-foreground">
              Enter للإرسال
            </span>
            <Button
              type="button"
              size="sm"
              onClick={handleSubmit}
              disabled={!text.trim() || isLoading}
              aria-label="إرسال السؤال"
              aria-disabled={!text.trim() || isLoading}
              className="h-8 px-3 rounded-xl gap-1.5 font-medium transition-all"
            >
              <span>إرسال</span>
              <Send className="size-3.5 rotate-180" aria-hidden="true" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
