"use client";

import { useState } from "react";
import { toast } from "sonner";
import { API_BASE_URL } from "@/lib/config";
import { authHeader } from "@/lib/auth";
import { Flashcard, QuizQuestion } from "@/lib/types";

// وظيفة واحدة: جلب إضافات الدرس (بطاقات/اختبار) — بدون أي عرض.
export type ExtrasKind = "cards" | "quiz";

export function useLessonExtras(topic: string) {
  const [cards, setCards] = useState<Flashcard[] | null>(null);
  const [quiz, setQuiz] = useState<QuizQuestion[] | null>(null);
  const [loading, setLoading] = useState<ExtrasKind | null>(null);

  const load = async (kind: ExtrasKind) => {
    setLoading(kind);
    try {
      const endpoint = kind === "cards" ? "/api/flashcards" : "/api/quiz";
      const r = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeader() },
        body: JSON.stringify({ topic }),
      });
      if (!r.ok) throw new Error(`فشل الطلب (${r.status})`);
      const j = await r.json();
      if (kind === "cards") setCards(j.cards ?? []);
      else setQuiz(j.quiz ?? []);
    } catch {
      toast.error(kind === "cards" ? "فشل توليد البطاقات" : "فشل توليد الاختبار");
    }
    setLoading(null);
  };

  return { cards, quiz, loading, load };
}
