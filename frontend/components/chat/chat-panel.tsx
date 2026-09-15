"use client";

import { useRef, type ReactNode } from "react";
import { ArrowDown, PanelRightOpen } from "lucide-react";
import { ChatHeader } from "./chat-header";
import { ChatInput } from "./chat-input";
import { ClarificationChips } from "./clarification-chips";
import { MessageItem } from "./message-item";
import { ThinkingIndicator } from "./thinking-indicator";
import { useSidebarControls } from "./assistant-shell";
import { useStickBottom } from "@/hooks/use-stick-bottom";
import type { ChatEngine } from "@/hooks/useChatEngine";
import type { StatsResponse } from "@/lib/types";

interface ChatPanelProps {
  stats: StatsResponse | null;
  engine: ChatEngine;
  /** ما يظهر عند فراغ المحادثة: اقتراحات البدء أو مؤشر التحميل */
  emptyState?: ReactNode;
}

// الهيكل البصري الوحيد لمنطقة المحادثة — يستقبل المحرك جاهزاً بلا منطق جلب.
export function ChatPanel({ stats, engine, emptyState }: ChatPanelProps) {
  const { messages, isLoading, streamStatus, clarify, lastFailed, send, sendClarification } = engine;
  const { desktopSidebar, setDesktopSidebar, openMenu } = useSidebarControls();
  const { mainRef, showJump, handleScroll, jumpToBottom } = useStickBottom(messages);
  const scrollBottomRef = useRef<HTMLDivElement>(null);

  return (
    <div className="flex-1 flex flex-col min-w-0 relative">
      <ChatHeader
        stats={stats}
        onOpenMenu={openMenu}
        status={isLoading ? "generating" : messages.length > 0 ? "done" : "idle"}
        sidebarOpen={desktopSidebar}
      />

      {/* زر فتح صريح يظهر فقط عند طي السايدبار — شاشات كبيرة */}
      {!desktopSidebar && (
        <button
          type="button"
          onClick={() => setDesktopSidebar(true)}
          aria-label="فتح قائمة المحادثات"
          title="فتح قائمة المحادثات"
          className="hidden lg:flex fixed top-16 right-3 z-30 size-9 rounded-full border border-border bg-background shadow-md text-muted-foreground hover:text-foreground items-center justify-center"
        >
          <PanelRightOpen className="size-4" />
        </button>
      )}

      <main ref={mainRef} onScroll={handleScroll} className="flex-1 overflow-y-auto overscroll-contain px-3 sm:px-6 py-4 sm:py-6 [scrollbar-gutter:stable]">
        <div className="max-w-2xl mx-auto">
          {messages.length === 0 ? (
            <div className="my-auto py-8">{emptyState}</div>
          ) : (
            <div className="space-y-3 pt-4 pb-20">
              {messages.map((msg) => (
                <MessageItem key={msg.id} message={msg} />
              ))}
              {clarify && <ClarificationChips question={clarify.question} options={clarify.options} onSelect={sendClarification} />}
              {isLoading && ![...messages].reverse().find((m) => m.role === "assistant")?.content && <ThinkingIndicator message={streamStatus || undefined} />}
              {lastFailed && !isLoading && (
                <div className="flex justify-center my-3">
                  <button onClick={() => send(lastFailed)} className="bg-destructive text-destructive-foreground px-4 py-2 rounded-full text-sm font-bold shadow hover:bg-destructive/90">حدث خطأ — اضغط Retry</button>
                </div>
              )}
              <div ref={scrollBottomRef} />
            </div>
          )}
        </div>
      </main>

      {showJump && messages.length > 0 && (
          <button
            type="button"
            onClick={jumpToBottom}
          aria-label="العودة لآخر الرد"
          className="absolute bottom-32 left-1/2 -translate-x-1/2 z-30 flex items-center gap-1.5 rounded-full border border-border bg-background px-3 py-1.5 text-xs font-semibold shadow-md hover:bg-muted"
        >
          <ArrowDown className="size-3.5" />
          آخر الرد
        </button>
      )}

      {/* Input — inside the flex flow, no overlap */}
      <footer className="border-t border-border/60 bg-background shrink-0 pb-[env(safe-area-inset-bottom)]">
        <ChatInput onSend={send} isLoading={isLoading} />
      </footer>
    </div>
  );
}
