import { ChatContainer } from "@/components/chat/chat-container";
import { API_BASE_URL } from "@/lib/config";
import { StatsResponse } from "@/lib/types";

async function getInitialStats(): Promise<StatsResponse | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/stats`, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}

export default async function AssistantPage() {
  const initialStats = await getInitialStats();
  return <ChatContainer initialStats={initialStats} />;
}
