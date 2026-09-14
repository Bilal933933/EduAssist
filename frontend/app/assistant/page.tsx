import { NewChatView } from "@/components/chat/chat-views";
import { SERVER_API_BASE_URL } from "@/lib/config";
import { StatsResponse } from "@/lib/types";

async function getInitialStats(): Promise<StatsResponse | null> {
  try {
    const res = await fetch(`${SERVER_API_BASE_URL}/api/stats`, { cache: "no-store" });
    if (!res.ok) return null;
    const j = await res.json();
    return (j?.ok === true ? j.data : j) as StatsResponse;
  } catch { return null; }
}

// بدء محادثة جديدة فقط — المحادثات المحفوظة في /assistant/[threadId].
export default async function AssistantPage() {
  const initialStats = await getInitialStats();
  return <NewChatView initialStats={initialStats} />;
}
