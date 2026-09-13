import { ChatResponse, ChatThread, StatsResponse, StoredMessage } from "@/lib/types";
import { authHeader } from "@/lib/auth";
import { API_BASE_URL } from "@/lib/config";

export async function fetchThreads(): Promise<ChatThread[]> {
  const response = await fetch(`${API_BASE_URL}/api/threads`, {
    headers: authHeader(),
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch threads: ${response.statusText}`);
  }
  const data = await response.json();
  return data.threads;
}

export async function fetchThreadMessages(
  threadId: number
): Promise<StoredMessage[]> {
  const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}/messages`, {
    headers: authHeader(),
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch messages: ${response.statusText}`);
  }
  const data = await response.json();
  return data.messages;
}

export async function deleteThread(threadId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}`, {
    method: "DELETE",
    headers: authHeader(),
  });
  if (!response.ok) {
    throw new Error(`Failed to delete thread: ${response.statusText}`);
  }
}

export async function fetchStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/stats`);

  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.statusText}`);
  }

  return response.json();
}

export async function* streamChat(question: string, threadId: number | null, onStatus?: (msg: string) => void) {
  const res = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify({ question, thread_id: threadId }),
  });
  if (!res.ok || !res.body) throw new Error(`Stream failed: ${res.status}`);
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const data = JSON.parse(line.slice(6));
      if (data.type === "status" && onStatus) onStatus(data.message);
      yield data;
    }
  }
}
