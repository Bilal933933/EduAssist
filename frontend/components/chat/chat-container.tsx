"use client";

import { useState, useRef, useEffect } from "react";
import { ChatHeader } from "./chat-header";
import { ChatSidebar } from "./chat-sidebar";
import { MessageItem } from "./message-item";
import { ThinkingIndicator } from "./thinking-indicator";
import { QuickPrompts } from "./quick-prompts";
import { ChatInput } from "./chat-input";
import { AuthPanel } from "@/components/auth/auth-panel";
import { Spinner } from "@/components/ui/spinner";
import { ClarificationChips } from "./clarification-chips";
import { ChatMessage, ChatThread, StatsResponse, StoredMessage } from "@/lib/types";
import { deleteThread, fetchStats, fetchThreadMessages, fetchThreads } from "@/lib/api";
import { getAuthToken } from "@/lib/auth";
import { useChatSocket } from "@/hooks/useChatSocket";
import { useChatStream } from "@/hooks/useChatStream";
import { toast } from "sonner";

interface ChatContainerProps {
  initialStats: StatsResponse | null;
}

export function ChatContainer({ initialStats }: ChatContainerProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState<StatsResponse | null>(initialStats);
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [currentThreadId, setCurrentThreadId] = useState<number | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [authState, setAuthState] = useState<"checking" | "guest" | "authed">("checking");
  const [clarify, setClarify] = useState<{ question: string; options: string[] } | null>(null);
  const [lastFailed, setLastFailed] = useState<string | null>(null);
  const { status: streamStatus, setStatus: setStreamStatus, stream } = useChatStream();
  const scrollBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setAuthState(getAuthToken() ? "authed" : "guest");
  }, []);

  const { send: sendSocket } = useChatSocket(
    authState === "authed",
    (data) => {
      setIsLoading(false);
      setMessages((prev) => [...prev, { id: `assistant-${Date.now()}`, content: data.answer, role: "assistant", createdAt: new Date(), hits: data.hits || [] }]);
      if (data.thread_id != null) setCurrentThreadId(data.thread_id);
      refreshThreads();
    },
    (msg) => {
      setIsLoading(false);
      setStreamStatus(null);
      toast.error(msg);
    }
  );

  // Auto scroll — performant: auto during streaming, smooth only on finalize, and only if user near bottom
  useEffect(() => {
    const el = scrollBottomRef.current;
    if (!el) return;
    const container = el.closest("main") as HTMLElement | null;
    if (container) {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 160;
      if (!isNearBottom) return;
    }
    const behavior: ScrollBehavior = isLoading ? "auto" : "smooth";
    requestAnimationFrame(() => {
      el.scrollIntoView({ behavior, block: "end" });
    });
  }, [messages, isLoading]);

  // Fetch updated stats if not available
  useEffect(() => {
    if (!stats) {
      fetchStats()
        .then(setStats)
        .catch((err) => console.error("Could not load stats:", err));
    }
  }, [stats]);

  const refreshThreads = () => {
    if (!getAuthToken()) return;
    fetchThreads()
      .then(setThreads)
      .catch((err) => console.error("Could not load threads:", err));
  };

  // Load previous conversations list only after auth is confirmed
  useEffect(() => {
    if (authState === "authed") refreshThreads();
  }, [authState]);

  // تحويل رسالة محفوظة من قاعدة البيانات إلى رسالة واجهة
  const mapStoredMessage = (m: StoredMessage): ChatMessage => ({
    id: `db-${m.id}`,
    content: m.content,
    role: m.role,
    createdAt: m.created_at ? new Date(m.created_at) : new Date(),
    hits: m.sources ?? undefined,
  });

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;
    setLastFailed(null);

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      content: text.trim(),
      role: "user",
      createdAt: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setStreamStatus("يفكك السؤال...");

    try {
      const assistantId = `assistant-${Date.now()}`;
      let fullText = "";
      let finalHits: any[] = [];
      let finalThreadId: number | null = null;
      setMessages((prev) => [...prev, { id: assistantId, content: "", role: "assistant", createdAt: new Date(), hits: [] }]);
      for await (const event of (await import("@/lib/api")).streamChat(text.trim(), currentThreadId, (msg) => setStreamStatus(msg)) as any) {
        if (event.type === "status") setStreamStatus(event.message);
        else if (event.type === "clarification") {
          setClarify({ question: event.question, options: event.options });
          setMessages((prev) => prev.filter((m) => m.id !== assistantId));
          setIsLoading(false);
          setStreamStatus(null);
          return;
        } else if (event.type === "answer_chunk") {
          fullText += event.text;
          setStreamStatus(null);
          setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, content: fullText } : m)));
        } else if (event.type === "done") {
          finalHits = event.hits || [];
          setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, hits: finalHits } : m)));
        } else if (event.type === "thread") finalThreadId = event.thread_id;
        else if (event.type === "error") throw new Error(event.error);
      }
      setIsLoading(false);
      setStreamStatus(null);
      if (finalThreadId != null) setCurrentThreadId(finalThreadId);
      refreshThreads();
      return;
    } catch (e: any) {
      console.warn("SSE failed, fallback to socket", e);
      setMessages((prev) => prev.filter((m) => m.content !== ""));
      const msg = e?.message || "حدث خطأ أثناء معالجة سؤالك.";
      setLastFailed(text.trim());
      toast.error(msg + " اضغط Retry.");
    }

    if (!sendSocket(currentThreadId, text.trim())) {
      setIsLoading(false);
      setStreamStatus(null);
      setLastFailed(text.trim());
      toast.error("لا يوجد اتصال بالخادم. اضغط Retry.");
    }
  };

  // فتح محادثة سابقة: تحميل رسائلها من الخادم
  const handleSelectThread = async (id: number) => {
    if (isLoading || id === currentThreadId) return;
    try {
      const stored = await fetchThreadMessages(id);
      setMessages(stored.map(mapStoredMessage));
      setCurrentThreadId(id);
    } catch (error) {
      console.error("Load thread error:", error);
      toast.error("تعذر تحميل المحادثة المختارة.");
    }
  };

  // بدء محادثة جديدة فارغة (تُنشأ في الخادم عند أول سؤال)
  const handleNewChat = () => {
    setMessages([]);
    setCurrentThreadId(null);
    toast.info("تم بدء محادثة جديدة");
  };

  // حذف أي محادثة من الخادم (من القائمة الجانبية)
  const handleDeleteThread = async (id: number) => {
    if (isLoading) return;
    try {
      await deleteThread(id);
      toast.success("تم حذف المحادثة");
      if (id === currentThreadId) {
        setMessages([]);
        setCurrentThreadId(null);
      }
      refreshThreads();
    } catch (error) {
      console.error("Delete thread error:", error);
      toast.error("تعذر حذف المحادثة.");
    }
  };

  // بوابة المصادقة: زائر بدون جلسة ← شاشة الدخول بدل الواجهة
  if (authState !== "authed") {
    if (authState === "checking") {
      return (
        <div className="min-h-dvh flex items-center justify-center bg-background">
          <Spinner className="size-8" />
        </div>
      );
    }
    return <AuthPanel onSuccess={() => setAuthState("authed")} />;
  }

  return (
    <div className="flex h-dvh overflow-hidden bg-background">
      {/* Sidebar: desktop fixed, mobile drawer */}
      <ChatSidebar
        threads={threads}
        currentThreadId={currentThreadId}
        onSelectThread={handleSelectThread}
        onNewChat={handleNewChat}
        onDeleteThread={handleDeleteThread}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main column */}
      <div className="flex-1 flex flex-col min-w-0">
        <ChatHeader stats={stats} onOpenMenu={() => setSidebarOpen(true)} />

        <main className="flex-1 overflow-y-auto px-4 sm:px-6 py-6">
          <div className="max-w-4xl mx-auto min-h-full flex flex-col justify-between">
            {messages.length === 0 ? (
              <div className="my-auto py-8">
                <QuickPrompts
                  onSelectPrompt={handleSendMessage}
                  disabled={isLoading}
                />
              </div>
            ) : (
              <div className="space-y-3 py-4">
                {messages.map((msg) => (
                  <MessageItem key={msg.id} message={msg} />
                ))}
                {clarify && <ClarificationChips question={clarify.question} options={clarify.options} onSelect={(opt) => { setClarify(null); handleSendMessage(`أقصد: ${opt} — ${messages[messages.length-1]?.content || ""}`.slice(0,120)); }} />}
                {isLoading && <ThinkingIndicator message={streamStatus || undefined} />}
                {lastFailed && !isLoading && (
                  <div className="flex justify-center my-3">
                    <button onClick={() => handleSendMessage(lastFailed)} className="bg-destructive text-destructive-foreground px-4 py-2 rounded-full text-sm font-bold shadow hover:bg-destructive/90">حدث خطأ — اضغط Retry</button>
                  </div>
                )}
                <div ref={scrollBottomRef} />
              </div>
            )}
          </div>
        </main>

        {/* Input — inside the flex flow, no overlap */}
        <footer className="border-t border-border/60 bg-background shrink-0">
          <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
        </footer>
      </div>
    </div>
  );
}
