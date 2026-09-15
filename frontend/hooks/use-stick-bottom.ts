"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { ChatMessage } from "@/lib/types";

// وظيفة واحدة: الالتصاق بآخر الرد — تتبع السكرول + زر القفز — بلا أي عرض.
export function useStickBottom(messages: ChatMessage[]) {
  const mainRef = useRef<HTMLElement>(null);
  const stickBottomRef = useRef(true);
  const [showJump, setShowJump] = useState(false);

  // تتبع التصاق المستخدم بالأسفل — لا نتدخل بتمريره أبداً وهو يقرأ بالأعلى
  const handleScroll = useCallback(() => {
    const container = mainRef.current;
    if (!container) return;
    const { scrollTop, scrollHeight, clientHeight } = container;
    const stuck = scrollHeight - scrollTop - clientHeight < 120;
    stickBottomRef.current = stuck;
    setShowJump(!stuck);
  }, []);

  const jumpToBottom = useCallback(() => {
    const container = mainRef.current;
    if (!container) return;
    stickBottomRef.current = true;
    setShowJump(false);
    container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
  }, []);

  // تمرير للأسفل فقط إذا كان المستخدم ملتصقاً به أصلاً (يمنع القفز)
  useEffect(() => {
    if (!stickBottomRef.current) return;
    const container = mainRef.current;
    if (!container) return;
    requestAnimationFrame(() => {
      container.scrollTop = container.scrollHeight;
    });
  }, [messages]);

  return { mainRef, showJump, handleScroll, jumpToBottom };
}
