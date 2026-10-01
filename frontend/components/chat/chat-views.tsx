"use client";

import { useRef } from "react";
import { toast } from "sonner";
import { ChatPanel } from "./chat-panel";
import { QuickPrompts } from "./quick-prompts";
import { ThinkingIndicator } from "./thinking-indicator";
import { useChatEngine } from "@/hooks/useChatEngine";
import { useStats, useThreadMessages } from "@/lib/queries";
import type { StatsResponse } from "@/lib/types";

// /assistant — بدء محادثة جديدة فقط: اقتراحات + إدخال، وأول رد يثبّت مسارها.
// تثبيت المسار بتحديث الرابط فقط (بلا تنقل) — التنقل يفكّ التركيب ويمسح حالة البث.
export function NewChatView({ initialStats }: { initialStats: StatsResponse | null }) {
  const { data: stats } = useStats(initialStats);
  const engine = useChatEngine({
    threadId: null,
    onThreadCreated: (id) => window.history.replaceState(null, "", `/assistant/${id}`),
  });
  return (
    <ChatPanel
      stats={stats ?? null}
      engine={engine}
      emptyState={<QuickPrompts onSelectPrompt={engine.send} disabled={engine.isLoading} />}
    />
  );
}

// /assistant/[threadId] — عرض محادثة محفوظة: بذر من الخادم ثم متابعة.
export function ThreadChatView({
  initialStats,
  threadId,
}: {
  initialStats: StatsResponse | null;
  threadId: number;
}) {
  const { data: stats } = useStats(initialStats);
  const seedQuery = useThreadMessages(threadId);
  const engine = useChatEngine({ threadId, seed: seedQuery.data });

  const errorShownRef = useRef(false);
  if (seedQuery.isError && !errorShownRef.current) {
    errorShownRef.current = true;
    toast.error("تعذر تحميل المحادثة.");
  }

  return (
    <ChatPanel
      stats={stats ?? null}
      engine={engine}
      emptyState={seedQuery.isLoading ? <ThinkingIndicator message="تحميل المحادثة..." /> : null}
    />
  );
}
