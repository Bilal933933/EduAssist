import { Injectable, Logger } from "@nestjs/common";
import axios from "axios";
import { config } from "../config";

@Injectable()
export class AiProxyService {
  private readonly logger = new Logger(AiProxyService.name);

  private client() {
    return axios.create({
      baseURL: config.aiServiceUrl,
      timeout: config.aiTimeoutMs,
      headers: { "X-Internal-Key": config.internalApiKey },
    });
  }

  /** يسأل مخ الـ AI: سؤال الطالب ← إجابة كاملة مع المصادر */
  async ask(
    question: string,
    threadId: number | null,
  ): Promise<{ answer: string; hits: unknown[]; thread_id: number | null }> {
    for (let attempt = 1; attempt <= 2; attempt++) {
      try {
        const res = await this.client().post("/api/chat", {
          question,
          thread_id: threadId ?? null,
        });
        return res.data;
      } catch (err: any) {
        const code = err?.code || "";
        const networkError =
          code === "ECONNREFUSED" || code === "ETIMEDOUT" || code === "ECONNABORTED";
        if (networkError && attempt === 1) {
          this.logger.warn(`خدمة الـ AI لا تستجيب، إعادة محاولة واحدة... (${code})`);
          continue;
        }
        if (err.response) {
          // خطأ منطقي من بايثون نفسه (4xx/5xx) — لا تكرر المحاولة
          throw new Error(`AI_ERROR_${err.response.status}`);
        }
        throw new Error("AI_UNREACHABLE");
      }
    }
    throw new Error("AI_UNREACHABLE");
  }

  /** تمرير شفاف لطلبات REST الخاصة بالمحادثات من البايثون */
  async passthrough(method: "get" | "delete", path: string): Promise<unknown> {
    const res = await this.client().request({ method, url: path });
    return res.data;
  }

  async stream(body: any) {
    const res = await axios.post(`${config.aiServiceUrl}/api/chat/stream`, body, {
      headers: { "X-Internal-Key": config.internalApiKey },
      responseType: "stream",
      timeout: 120000,
    });
    return res.data;
  }

  async healthy(): Promise<boolean> {
    try {
      const res = await axios.get(`${config.aiServiceUrl}/health`, { timeout: 5000 });
      return res.status === 200;
    } catch {
      return false;
    }
  }
}
