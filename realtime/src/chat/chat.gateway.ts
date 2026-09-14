import { Logger, UseFilters } from "@nestjs/common";
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
import { AppError, messageFor } from "../common/errors";
import { WsExceptionFilter } from "../common/filters/ws-exception.filter";
import { getLogger } from "../common/logger";
import { AiProxyService } from "./ai-proxy.service";

interface AuthedSocket extends Socket {
  data: { userId: number; email: string };
}

@WebSocketGateway({ cors: { origin: true }, path: "/socket.io" })
@UseFilters(new WsExceptionFilter())
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
      client.emit("error", { code: "UNAUTHORIZED", message: messageFor("UNAUTHORIZED").message });
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
      client.emit("error", { code: "QUESTION_EMPTY", message: messageFor("QUESTION_EMPTY").message });
      return;
    }
    if (!this.allow(client.data.userId)) {
      client.emit("error", {
        code: "RATE_LIMITED",
        message: `تجاوزت حد الأسئلة (${config.rateLimitPerMin} في الدقيقة). انتظر قليلاً.`,
      });
      return;
    }
    try {
      const result = await this.ai.ask(question, body?.thread_id ?? null);
      client.emit("answer", result);
    } catch (err: any) {
      // أخطاء بأكواد بايثون نفسها — الفرونت يعرض message مباشرة
      const code = err instanceof AppError ? err.code : "INTERNAL_ERROR";
      const { message } = messageFor(code);
      getLogger("errors").error(JSON.stringify({ type: "ws_error", code, user: client.data.userId }));
      this.logger.error(`فشل سؤال من #${client.data.userId}: ${code}`);
      client.emit("error", { code, message, retryable: true });
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
