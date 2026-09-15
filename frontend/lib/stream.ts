import { API_BASE_URL } from "@/lib/config";
import { authHeader } from "@/lib/auth";
import { KnowledgeHit } from "@/lib/types";

/** حدث بث SSE من /api/chat/stream — يطابق ما يرسله الباك حرفياً */
export interface StreamEvent {
  type: "status" | "clarification" | "answer_chunk" | "answer_correct" | "done" | "thread" | "error" | string;
  message?: string;
  text?: string;
  question?: string;
  options?: string[];
  hits?: KnowledgeHit[];
  thread_id?: number;
  error?: string | { code?: string; message?: string };
}

/** يستخرج رسالة عربية من حدث error سواء كان نصاً أو كائناً {code,message} */
export function streamErrorMessage(error: StreamEvent["error"]): string {
  if (typeof error === "string" && error) return error;
  if (error && typeof error === "object" && error.message) return error.message;
  return "حدث خطأ أثناء معالجة سؤالك.";
}

export async function* streamChat(
  question: string,
  threadId: number | null,
  onStatus?: (msg: string) => void,
  signal?: AbortSignal
): AsyncGenerator<StreamEvent> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader() },
      body: JSON.stringify({ question, thread_id: threadId }),
      signal,
    });
  } catch (e) {
    if ((e as Error)?.name === "AbortError") return;
    throw new Error("تعذر الاتصال بالخادم. تحقق من الاتصال ثم اضغط Retry.");
  }
  if (!res.ok) {
    // الباك يعيد مغلف fail عربي {ok:false, error:{message}} — نعرض رسالته كما هي
    let msg = `فشل الطلب (${res.status})`;
    try {
      const j = await res.json();
      msg = (j as { error?: { message?: string } })?.error?.message || msg;
    } catch {
      /* الجسم ليس JSON — نُبقي الرسالة الافتراضية */
    }
    throw new Error(msg);
  }
  if (!res.body) throw new Error("تعذر بدء البث. اضغط Retry.");
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
      if (!line.startsWith("data:")) continue;
      let data: StreamEvent;
      try {
        data = JSON.parse(line.slice(5).trim()) as StreamEvent;
      } catch {
        continue; // سطر تالف واحد لا يقتل بثاً كاملاً
      }
      if (!data || typeof data.type !== "string") continue;
      if (data.type === "status" && onStatus) onStatus(data.message ?? "");
      yield data;
    }
  }
}
