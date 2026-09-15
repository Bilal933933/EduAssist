"use client";

import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { queryKeys } from "@/lib/queries";
import { streamChat, streamErrorMessage } from "@/lib/stream";
import { toArabicStepLabel } from "@/lib/agent-labels";
import { useChatSocket } from "@/hooks/useChatSocket";
import type { ChatMessage, KnowledgeHit, StoredMessage } from "@/lib/types";

export function toChatMessages(stored: StoredMessage[]): ChatMessage[] {
  return stored.map((m) => ({
    id: `db-${m.id}`,
    content: m.content,
    role: m.role,
    createdAt: m.created_at ? new Date(m.created_at) : new Date(),
    hits: m.sources ?? undefined,
  }));
}

interface EngineOptions {
  /** null = محادثة جديدة؛ رقم = محادثة من URL (مصدر الحقيقة) */
  threadId: number | null;
  /** رسائل الخادم لعرض المحادثة المحفوظة */
  seed?: StoredMessage[];
  /** يُستدعى عند إنشاء محادثة من /assistant لتثبيت مسارها */
  onThreadCreated?: (id: number) => void;
}

export interface ChatEngine {
  messages: ChatMessage[];
  isLoading: boolean;
  streamStatus: string | null;
  clarify: { question: string; options: string[] } | null;
  lastFailed: string | null;
  send: (text: string) => void;
  sendClarification: (opt: string) => void;
}

// محرك المحادثة الوحيد: SSE أولاً ثم سوكت احتياطياً — تشترك فيه الشاشتان.
export function useChatEngine({ threadId, seed, onThreadCreated }: EngineOptions): ChatEngine {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [clarify, setClarify] = useState<{ question: string; options: string[] } | null>(null);
  const [lastFailed, setLastFailed] = useState<string | null>(null);
  const [streamStatus, setStreamStatus] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const queryClient = useQueryClient();

  // إلغاء أي بث معلق عند مغادرة الشاشة — طلبات 30-60 ثانية لا تبقى يتيمة
  useEffect(() => {
    return () => abortRef.current?.abort();
  }, []);

  const refreshThreads = () =>
    queryClient.invalidateQueries({ queryKey: queryKeys.threads });

  // بذر رسائل المحادثة المحفوظة مرة واحدة لكل threadId (بلا fetch في useEffect).
  const seededForRef = useRef<number | null>(null);
  if (threadId != null && seed && seededForRef.current !== threadId) {
    seededForRef.current = threadId;
    const seeded = toChatMessages(seed);
    setMessages((prev) => (prev.length === 0 ? seeded : [...seeded, ...prev]));
  }

  // مراجع حية لكولباك السوكت (يُسجل مرة واحدة عند التركيب).
  const liveRef = useRef({ threadId, onThreadCreated });
  liveRef.current = { threadId, onThreadCreated };

  const { send: sendSocket } = useChatSocket({
    enabled: true,
    onAnswer: (data) => {
      setIsLoading(false);
      setStreamStatus(null);
      setMessages((prev) => [...prev, { id: `assistant-${Date.now()}`, content: data.answer, role: "assistant", createdAt: new Date(), hits: data.hits || [] }]);
      if (data.thread_id != null) liveRef.current.onThreadCreated?.(data.thread_id);
      refreshThreads();
    },
    onError: (msg) => {
      setIsLoading(false);
      setStreamStatus(null);
      toast.error(msg);
    },
  });

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;
    // إلغاء البث السابق قبل بدء الجديد — يمنع تداخل الردود
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLastFailed(null);
    setClarify(null);

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      content: text.trim(),
      role: "user",
      createdAt: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setStreamStatus("يفكك السؤال...");

    const assistantId = `assistant-${Date.now()}`;
    try {
      let fullText = "";
      let finalHits: KnowledgeHit[] = [];
      let finalThreadId: number | null = null;
      const startedAt = Date.now();
      const traceSteps: { label: string }[] = [];
      const pushStep = (label: string) => {
        if (!label) return;
        const key = toArabicStepLabel(label);
        if (traceSteps.some((s) => toArabicStepLabel(s.label) === key)) return;
        traceSteps.push({ label });
      };
      setMessages((prev) => [...prev, { id: assistantId, content: "", role: "assistant", createdAt: new Date(), hits: [], trace: [], streaming: true }]);
      for await (const event of streamChat(text.trim(), liveRef.current.threadId, (msg: string) => setStreamStatus(msg), controller.signal)) {
        if (event.type === "status") {
          setStreamStatus(event.message ?? null);
          pushStep(event.message ?? "");
          const snapshot = [...traceSteps];
          setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, trace: snapshot } : m)));
        }
        else if (event.type === "clarification") {
          setClarify({ question: event.question ?? "", options: event.options ?? [] });
          setMessages((prev) => prev.filter((m) => m.id !== assistantId));
          setIsLoading(false);
          setStreamStatus(null);
          return;
        } else if (event.type === "answer_chunk") {
          fullText += event.text ?? "";
          setStreamStatus(null);
          setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, content: fullText } : m)));
        } else if (event.type === "answer_correct") {
          // المصحِّح البعدي قد يعيد صياغة الإجابة بعد اكتمال البث.
          fullText = event.text ?? fullText;
          setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, content: fullText } : m)));
        } else if (event.type === "done") {
          finalHits = event.hits ?? [];
          const durationMs = Date.now() - startedAt;
          const snapshot = [...traceSteps];
          setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, hits: finalHits, trace: snapshot, durationMs, streaming: false } : m)));
        } else if (event.type === "thread") finalThreadId = event.thread_id ?? null;
        else if (event.type === "error") throw new Error(streamErrorMessage(event.error));
      }
      setIsLoading(false);
      setStreamStatus(null);
      setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, streaming: false, durationMs: m.durationMs ?? Date.now() - startedAt } : m)));
      if (/تعذّر الوصول|ضغط مؤقت|429|حدث خطأ/.test(fullText)) {
        setLastFailed(text.trim());
      }
      if (finalThreadId != null) liveRef.current.onThreadCreated?.(finalThreadId);
      refreshThreads();
      return;
    } catch (e: unknown) {
      if (controller.signal.aborted) return; // إلغاء مقصود — بلا toast كاذب ولا fallback مزدوج
      console.warn("SSE failed, fallback to socket", e);
      setMessages((prev) => prev.filter((m) => m.id !== assistantId));
      setStreamStatus(null);
      const msg = e instanceof Error ? e.message : "حدث خطأ أثناء معالجة سؤالك.";
      setLastFailed(text.trim());
      toast.error(msg + " اضغط Retry.");
    }

    if (!sendSocket(liveRef.current.threadId, text.trim())) {
      setIsLoading(false);
      setStreamStatus(null);
      setLastFailed(text.trim());
      toast.error("لا يوجد اتصال بالخادم. اضغط Retry.");
    }
  };

  const sendClarification = (opt: string) => {
    setClarify(null);
    const lastUser = [...messages].reverse().find((m) => m.role === "user");
    void handleSendMessage(`أقصد: ${opt} — ${lastUser?.content || ""}`.slice(0, 120));
  };

  return { messages, isLoading, streamStatus, clarify, lastFailed, send: handleSendMessage, sendClarification };
}
