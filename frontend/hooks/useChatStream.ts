"use client";
import { useState, useCallback } from "react";
import { API_BASE_URL } from "@/lib/config";
import { authHeader } from "@/lib/auth";

export function useChatStream() {
  const [status, setStatus] = useState<string | null>(null);
  const [steps, setSteps] = useState<{ label: string }[]>([]);
  const [durationMs, setDurationMs] = useState<number | undefined>(undefined);

  const stream = useCallback(async (
    question: string,
    threadId: number | null,
    onChunk: (text: string) => void,
    onDone: (hits: any[], threadId: number | null) => void
  ) => {
    const res = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader() },
      body: JSON.stringify({ question, thread_id: threadId }),
    });
    if (!res.ok || !res.body) throw new Error(`Stream failed ${res.status}`);
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let finalHits: any[] = [];
    let finalThreadId: number | null = null;
    const startedAt = Date.now();
    setSteps([]);
    setDurationMs(undefined);

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const data = JSON.parse(line.slice(6));
        if (data.type === "status") {
          setStatus(data.message);
          setSteps((prev) => (prev[prev.length - 1]?.label === data.message ? prev : [...prev, { label: data.message }]));
        }
        else if (data.type === "answer_chunk") {
          setStatus(null);
          onChunk(data.text);
        } else if (data.type === "done") finalHits = data.hits || [];
        else if (data.type === "thread") finalThreadId = data.thread_id;
        else if (data.type === "error") throw new Error(data.error);
      }
    }
    setStatus(null);
    setDurationMs(Date.now() - startedAt);
    onDone(finalHits, finalThreadId);
  }, []);

  return { status, setStatus, steps, durationMs, stream };
}
