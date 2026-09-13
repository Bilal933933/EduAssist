"use client";

import { useState } from "react";
import { toast } from "sonner";
import { API_BASE_URL } from "@/lib/config";
import { authHeader } from "@/lib/auth";

// وظيفة واحدة: جلب إضافات الدرس (بطاقات/اختبار) — بدون أي عرض.
export type ExtrasKind = "cards" | "quiz";

export function useLessonExtras(topic: string) {
  const [cards, setCards] = useState<any[] | null>(null);
  const [quiz, setQuiz] = useState<any[] | null>(null);
  const [loading, setLoading] = useState<ExtrasKind | null>(null);

  const load = async (kind: ExtrasKind) => {
    setLoading(kind);
    try {
      const endpoint = kind === "cards" ? "/api/flashcards" : "/api/quiz";
      const key = kind === "cards" ? "cards" : "quiz";
      const r = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeader() },
        body: JSON.stringify({ topic }),
      });
      const j = await r.json();
      if (kind === "cards") setCards(j.cards);
      else setQuiz(j.quiz);
    } catch {
      toast.error(kind === "cards" ? "فشل توليد البطاقات" : "فشل توليد الاختبار");
    }
    setLoading(null);
  };

  return { cards, quiz, loading, load };
}
