"use client";
import { useEffect, useRef } from "react";
import { io, type Socket } from "socket.io-client";
import { API_BASE_URL } from "@/lib/config";
import { getAuthToken } from "@/lib/auth";
import { ChatResponse } from "@/lib/types";
import { toast } from "sonner";

export function useChatSocket(
  enabled: boolean,
  onAnswer: (data: ChatResponse) => void,
  onError: (msg: string) => void
) {
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    if (!enabled) return;
    const socket = io(API_BASE_URL, { auth: { token: getAuthToken() || "" }, reconnectionDelayMax: 10000 });
    socketRef.current = socket;
    socket.on("answer", onAnswer);
    socket.on("error", (e: { message?: string }) => onError(e.message || "خطأ"));
    return () => { socket.disconnect(); socketRef.current = null; };
  }, [enabled]);

  const send = (threadId: number | null, question: string) => {
    const s = socketRef.current;
    if (!s || !s.connected) { onError("لا يوجد اتصال"); return false; }
    s.emit("question", { thread_id: threadId, question });
    return true;
  };

  return { send, socketRef };
}
