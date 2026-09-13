"use client";

import { useState } from "react";
import { Sparkles, Copy, Check, Layers, HelpCircle } from "lucide-react";
import { ChatMessage } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { FormattedText } from "./formatted-text";
import { MessageSources } from "./message-sources";
import { toast } from "sonner";
import { useState as useState2 } from "react";
import { API_BASE_URL } from "@/lib/config";
import { authHeader } from "@/lib/auth";

interface AssistantMessageProps {
  message: ChatMessage;
  formattedTime: string | null;
}

export function AssistantMessage({ message, formattedTime }: AssistantMessageProps) {
  const [copied, setCopied] = useState(false);
  const [cards, setCards] = useState<any[] | null>(null);
  const [quiz, setQuiz] = useState<any[] | null>(null);
  const [loading, setLoading] = useState<"cards" | "quiz" | null>(null);

  const topic = message.content.match(/درس\s+(\S+)/)?.[1] || "الفاعل";

  const handleCards = async () => {
    setLoading("cards");
    try {
      const r = await fetch(`${API_BASE_URL}/api/flashcards`, { method: "POST", headers: { "Content-Type": "application/json", ...authHeader() }, body: JSON.stringify({ topic }) });
      const j = await r.json(); setCards(j.cards);
    } catch { toast.error("فشل توليد البطاقات"); }
    setLoading(null);
  };
  const handleQuiz = async () => {
    setLoading("quiz");
    try {
      const r = await fetch(`${API_BASE_URL}/api/quiz`, { method: "POST", headers: { "Content-Type": "application/json", ...authHeader() }, body: JSON.stringify({ topic }) });
      const j = await r.json(); setQuiz(j.quiz);
    } catch { toast.error("فشل توليد الاختبار"); }
    setLoading(null);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      toast.success("تم نسخ الإجابة إلى الحافظة");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("فشل نسخ النص");
    }
  };

  return (
    <div className="flex justify-end items-start gap-3 my-6 group">
      <div className="flex flex-col items-start max-w-[92%] sm:max-w-[85%] w-full space-y-3" dir="rtl">
        <div className="w-full bg-card border border-border/80 rounded-2xl rounded-tl-none p-5 sm:p-6 shadow-sm hover:shadow-md transition-shadow space-y-4 text-card-foreground relative ring-1 ring-border/50 text-right">
          
          <FormattedText content={message.content} />

          <div className="flex items-center justify-between pt-3 border-t border-border/60 text-xs text-muted-foreground flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={handleCopy} className="h-7 px-2.5 text-xs gap-1.5">
                {copied ? <><Check className="size-3.5 text-emerald-600" /><span>تم النسخ</span></> : <><Copy className="size-3.5" /><span>نسخ</span></>}
              </Button>
              <Button variant="outline" size="sm" onClick={handleCards} disabled={!!loading} className="h-7 text-xs gap-1">
                <Layers className="size-3.5" />{loading==="cards" ? "..." : "بطاقات"}
              </Button>
              <Button variant="outline" size="sm" onClick={handleQuiz} disabled={!!loading} className="h-7 text-xs gap-1">
                <HelpCircle className="size-3.5" />{loading==="quiz" ? "..." : "اختبار"}
              </Button>
            </div>
            {formattedTime && <span className="text-[11px] font-medium">{formattedTime}</span>}
          </div>
          {cards && <div className="mt-3 space-y-2">{cards.map((c,i)=><div key={i} className="p-3 rounded-xl bg-secondary/50 border text-sm"><b>س{i+1}:</b> {c.q}<br/><span className="text-primary">ج: {c.a}</span></div>)}</div>}
          {quiz && <div className="mt-3 space-y-2">{quiz.map((q,i)=><div key={i} className="p-3 rounded-xl bg-secondary/50 border text-sm"><b>س{i+1}:</b> {q.q}<div className="grid grid-cols-2 gap-1 mt-1">{q.options.map((o:string,idx:number)=><span key={idx} className={idx===q.answer ? "text-emerald-700 font-bold" : ""}>{idx+1}. {o}</span>)}</div><span className="text-xs text-muted-foreground">{q.explain}</span></div>)}</div>}

          <MessageSources hits={message.hits || []} />
        </div>
      </div>

      <div className="size-9 rounded-full bg-gradient-to-tr from-primary to-emerald-700 text-white flex items-center justify-center shrink-0 mt-1 shadow-md ring-2 ring-primary/20">
        <Sparkles className="size-4 text-amber-300" />
      </div>
    </div>
  );
}
