import { ChatContainer } from "@/components/chat/chat-container";
import { StatsResponse } from "@/lib/types";

async function getInitialStats(): Promise<StatsResponse | null> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  try {
    const res = await fetch(`${apiUrl}/api/stats`, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}

export default async function AssistantPage() {
  const initialStats = await getInitialStats();
  return <ChatContainer initialStats={initialStats} />;
}
