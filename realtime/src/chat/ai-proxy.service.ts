import { Injectable, Logger } from "@nestjs/common";
import axios from "axios";
import { AppError } from "../common/errors";
import { getRequestId } from "../common/request-context";
import { isEnvelope } from "../common/response";
import { config } from "../config";

@Injectable()
export class AiProxyService {
  private readonly logger = new Logger(AiProxyService.name);

  private client() {
    return axios.create({
      baseURL: config.aiServiceUrl,
      timeout: config.aiTimeoutMs,
      headers: {
        "X-Internal-Key": config.internalApiKey,
        // نفس requestId يعبر Realtime → بايثون لتتبع واحد
        ...(getRequestId() ? { "X-Request-Id": getRequestId() as string } : {}),
      },
    });
  }

  /** يسأل مخ الـ AI: سؤال الطالب ← إجابة كاملة مع المصادر (يفك مغلف بايثون) */
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
        // بايثون يرد بمغلف {ok,data} — نفك data ليبقى حدث السوكت كما كان
        if (isEnvelope(res.data)) {
          if (res.data.ok) return res.data.data as { answer: string; hits: unknown[]; thread_id: number | null };
          throw new AppError(res.data.error.code);
        }
        return res.data;
      } catch (err: any) {
        if (err instanceof AppError) throw err; // خطأ منطقي من بايثون — لا تكرر
        const code = err?.code || "";
        const networkError =
          code === "ECONNREFUSED" || code === "ETIMEDOUT" || code === "ECONNABORTED";
        if (networkError && attempt === 1) {
          this.logger.warn(`خدمة الـ AI لا تستجيب، إعادة محاولة واحدة... (${code})`);
          continue;
        }
        if (err.response) {
          // مغلف بايثون مر عبر الفلتر؟ نرمي كوده مباشرة
          if (isEnvelope(err.response.data) && !err.response.data.ok) {
            throw new AppError(err.response.data.error.code);
          }
          // بايثون يرد بالحالة 429 عند نفاد الحصة — نمرر نفس الكود بدل التعميم
          if (err.response.status === 429) {
            throw new AppError("QUOTA_EXHAUSTED");
          }
          // خطأ منطقي من بايثون نفسه (4xx/5xx) — لا تكرر المحاولة
          throw new AppError("INTERNAL_ERROR");
        }
        throw new AppError("AI_UNREACHABLE");
      }
    }
    throw new AppError("AI_UNREACHABLE");
  }

  /** تمرير شفاف لطلبات REST من البايثون (محادثات/إضافات/ذاكرة) — المغلف يُمرر كما هو */
  async passthrough(
    method: "get" | "delete" | "post",
    path: string,
    body?: unknown,
  ): Promise<unknown> {
    const res = await this.client().request({ method, url: path, data: body });
    return res.data;
  }

  async stream(body: any) {
    const res = await axios.post(`${config.aiServiceUrl}/api/chat/stream`, body, {
      headers: {
        "X-Internal-Key": config.internalApiKey,
        ...(getRequestId() ? { "X-Request-Id": getRequestId() as string } : {}),
      },
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
