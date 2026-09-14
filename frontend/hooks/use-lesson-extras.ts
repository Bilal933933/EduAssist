"use client";

import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { fetchFlashcards, fetchQuiz } from "@/lib/api";
import { Flashcard, QuizQuestion } from "@/lib/types";

// وظيفة واحدة: حالة إضافات الدرس (بطاقات/اختبار) — الجلب في lib/api.
export type ExtrasKind = "cards" | "quiz";

export function useLessonExtras(topic: string) {
  const [cards, setCards] = useState<Flashcard[] | null>(null);
  const [quiz, setQuiz] = useState<QuizQuestion[] | null>(null);
  const [loading, setLoading] = useState<ExtrasKind | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => abortRef.current?.abort();
  }, []);

  const load = async (kind: ExtrasKind) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(kind);
    try {
      if (kind === "cards") setCards((await fetchFlashcards(topic, controller.signal)).cards ?? []);
      else setQuiz((await fetchQuiz(topic, controller.signal)).quiz ?? []);
    } catch (e) {
      if (controller.signal.aborted) return; // إلغاء مقصود — بلا toast كاذب
      toast.error(e instanceof Error ? e.message : kind === "cards" ? "فشل توليد البطاقات" : "فشل توليد الاختبار");
    }
    if (!controller.signal.aborted) setLoading(null);
  };

  return { cards, quiz, loading, load };
}
