import { Logger } from "@nestjs/common";
import {
  ConnectedSocket,
  MessageBody,
  OnGatewayConnection,
  OnGatewayDisconnect,
  SubscribeMessage,
  WebSocketGateway,
  WebSocketServer,
} from "@nestjs/websockets";
import { Server, Socket } from "socket.io";
import { config } from "../config";
import { verifyToken } from "../auth/jwt.util";
import { AiProxyService } from "./ai-proxy.service";

interface AuthedSocket extends Socket {
  data: { userId: number; email: string };
}

@WebSocketGateway({ cors: { origin: true }, path: "/socket.io" })
export class ChatGateway implements OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer() server!: Server;

  private readonly logger = new Logger(ChatGateway.name);
  /** نافذة منزلقة في الذاكرة: userId → طوابع زمنية للأسئلة */
  private readonly hits = new Map<number, number[]>();

  constructor(private readonly ai: AiProxyService) {}

  handleConnection(client: AuthedSocket): void {
    const raw = (client.handshake.auth?.token as string) || "";
    const payload = raw ? verifyToken(raw.replace(/^Bearer\s+/i, "")) : null;
    if (!payload) {
      client.emit("error", { message: "غير مصرح: توكن مفقود أو غير صالح." });
      client.disconnect(true);
      return;
    }
    client.data = { userId: payload.sub, email: payload.email };
    this.logger.log(`طالب متصل: ${payload.email} (#${payload.sub})`);
  }

  handleDisconnect(client: AuthedSocket): void {
    if (client.data?.email) {
      this.logger.log(`طالب انقطع: ${client.data.email}`);
    }
  }

  @SubscribeMessage("question")
  async handleQuestion(
    @ConnectedSocket() client: AuthedSocket,
    @MessageBody() body: { thread_id?: number | null; question?: string },
  ) {
    const question = (body?.question || "").trim();
    if (!question) {
      client.emit("error", { message: "السؤال فارغ." });
      return;
    }
    if (!this.allow(client.data.userId)) {
      client.emit("error", {
        message: `تجاوزت حد الأسئلة (${config.rateLimitPerMin} في الدقيقة). انتظر قليلاً.`,
      });
      return;
    }
    try {
      const result = await this.ai.ask(question, body?.thread_id ?? null);
      client.emit("answer", result);
    } catch (err: any) {
      const isTimeout = err?.code === "ECONNABORTED" || err?.message?.includes("timeout");
      const message = isTimeout
        ? "انتهت مهلة المعالجة (60 ثانية). تم حفظ ما وصل - اضغط Retry للمحاولة."
        : err?.message === "AI_UNREACHABLE"
        ? "خدمة الذكاء الاصطناعي غير متاحة حالياً. حاول بعد قليل."
        : "حدث خطأ أثناء معالجة سؤالك. اضغط Retry.";
      this.logger.error(`فشل سؤال من #${client.data.userId}: ${err?.message} code=${err?.code}`);
      client.emit("error", { message, retryable: true });
    }
  }

  /** Rate Limit بسيط: N أسئلة كحد أقصى في الدقيقة لكل طالب */
  private allow(userId: number): boolean {
    const now = Date.now();
    const windowMs = 60_000;
    const list = (this.hits.get(userId) || []).filter((t) => now - t < windowMs);
    if (list.length >= config.rateLimitPerMin) {
      this.hits.set(userId, list);
      return false;
    }
    list.push(now);
    this.hits.set(userId, list);
    return true;
  }
}
