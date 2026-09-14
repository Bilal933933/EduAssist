import { ChatThread, FlashcardsResponse, MemoryResponse, QuizResponse, StatsResponse, StoredMessage } from "@/lib/types";
import { authHeader } from "@/lib/auth";
import { API_BASE_URL } from "@/lib/config";
import { unwrap } from "@/lib/envelope";

export async function fetchThreads(): Promise<ChatThread[]> {
  const response = await fetch(`${API_BASE_URL}/api/threads`, {
    headers: authHeader(),
  });
  const data = await unwrap<{ threads: ChatThread[] }>(response);
  return (data as { threads: ChatThread[] }).threads ?? (data as unknown as ChatThread[]);
}

export async function fetchThreadMessages(
  threadId: number
): Promise<StoredMessage[]> {
  const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}/messages`, {
    headers: authHeader(),
  });
  const data = await unwrap<{ thread_id: number; messages: StoredMessage[] }>(response);
  return (data as { messages: StoredMessage[] }).messages ?? (data as unknown as StoredMessage[]);
}

export async function deleteThread(threadId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}`, {
    method: "DELETE",
    headers: authHeader(),
  });
  if (!response.ok && response.status !== 204) {
    await unwrap<unknown>(response);
  }
}

export async function fetchStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/stats`);

  return unwrap<StatsResponse>(response);
}

export async function fetchMemory(grade?: string): Promise<MemoryResponse> {
  const qs = grade ? `?grade=${encodeURIComponent(grade)}` : "";
  const response = await fetch(`${API_BASE_URL}/api/memory${qs}`, {
    headers: authHeader(),
  });
  return unwrap<MemoryResponse>(response);
}

export async function fetchFlashcards(topic: string, signal?: AbortSignal): Promise<FlashcardsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/flashcards`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify({ topic }),
    signal,
  });
  return unwrap<FlashcardsResponse>(response);
}

export async function fetchQuiz(topic: string, signal?: AbortSignal): Promise<QuizResponse> {
  const response = await fetch(`${API_BASE_URL}/api/quiz`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify({ topic }),
    signal,
  });
  return unwrap<QuizResponse>(response);
}
