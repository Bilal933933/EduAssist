"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { io, type Socket } from "socket.io-client";
import { API_BASE_URL } from "@/lib/config";
import { getAuthToken } from "@/lib/auth";
import type { ChatResponse } from "@/lib/types";

interface ChatSocketOptions {
  enabled: boolean;
  onAnswer: (data: ChatResponse) => void;
  onError: (msg: string) => void;
}

// وظيفة واحدة: قناة السوكت الاحتياطية — اتصال واحد + حالة + إرسال. الكولباك عبر liveRef بلا stale closure.
export function useChatSocket({ enabled, onAnswer, onError }: ChatSocketOptions) {
  const socketRef = useRef<Socket | null>(null);
  const [connected, setConnected] = useState(false);

  // مراجع حية — التسجيل على السوكت مرة واحدة عند التركيب
  const liveRef = useRef({ onAnswer, onError });
  liveRef.current = { onAnswer, onError };

  useEffect(() => {
    if (!enabled) return;
    const socket = io(API_BASE_URL, {
      auth: { token: getAuthToken() || "" },
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 10000,
    });
    socketRef.current = socket;
    socket.on("connect", () => setConnected(true));
    socket.on("disconnect", () => setConnected(false));
    socket.on("connect_error", () => setConnected(false));
    socket.on("answer", (data: ChatResponse) => liveRef.current.onAnswer(data));
    socket.on("error", (e: { message?: string }) =>
      liveRef.current.onError(e?.message || "خطأ")
    );
    return () => {
      socket.disconnect();
      socketRef.current = null;
      setConnected(false);
    };
  }, [enabled]);

  const send = useCallback(
    (threadId: number | null, question: string) => {
      const s = socketRef.current;
      if (!s || !s.connected) {
        liveRef.current.onError("لا يوجد اتصال");
        return false;
      }
      s.emit("question", { thread_id: threadId, question });
      return true;
    },
    []
  );

  return { send, connected };
}
