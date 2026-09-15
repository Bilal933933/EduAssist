import { notFound } from "next/navigation";
import { ThreadChatView } from "@/components/chat/chat-views";
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

export default async function ThreadPage({
  params,
}: {
  params: Promise<{ threadId: string }>;
}) {
  const { threadId } = await params;
  const id = Number(threadId);
  if (!Number.isInteger(id) || id <= 0) notFound();
  const initialStats = await getInitialStats();
  return <ThreadChatView initialStats={initialStats} threadId={id} />;
}
