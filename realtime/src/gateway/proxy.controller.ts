import {
  Controller,
  Delete,
  Get,
  HttpCode,
  Param,
  ParseIntPipe,
  Post,
  Req,
  Res,
  UnauthorizedException,
} from "@nestjs/common";
import type { Request, Response } from "express";
import { AiProxyService } from "../chat/ai-proxy.service";
import { verifyToken } from "../auth/jwt.util";

/**
 * بوابة تمرير شفاف لمسارات REST الخاصة بالمحادثات المخزنة في خدمة الـ AI.
 * الفرونت لا يعرف بوجود البايثون — كل شيء يمر من هنا.
 */
@Controller("api")
export class ProxyController {
  constructor(private readonly ai: AiProxyService) {}

  /** مسارات المحادثات شخصية → تتطلب توكن طالب صالح */
  private requireStudent(req: Request): void {
    const header = req.headers.authorization || "";
    const payload = verifyToken(header.replace(/^Bearer\s+/i, ""));
    if (!payload) {
      throw new UnauthorizedException("توكن مفقود أو منتهي.");
    }
  }

  @Get("threads")
  listThreads(@Req() req: Request) {
    this.requireStudent(req);
    return this.ai.passthrough("get", "/api/threads");
  }

  @Get("threads/:id/messages")
  threadMessages(@Req() req: Request, @Param("id", ParseIntPipe) id: number) {
    this.requireStudent(req);
    return this.ai.passthrough("get", `/api/threads/${id}/messages`);
  }

  @Delete("threads/:id")
  @HttpCode(204)
  async deleteThread(@Req() req: Request, @Param("id", ParseIntPipe) id: number) {
    this.requireStudent(req);
    await this.ai.passthrough("delete", `/api/threads/${id}`);
  }

  @Post("chat/stream")
  async chatStream(@Req() req: Request, @Res() res: Response) {
    this.requireStudent(req);
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    const stream = await this.ai.stream(req.body);
    stream.on("data", (chunk: Buffer) => res.write(chunk));
    stream.on("end", () => res.end());
    stream.on("error", () => res.end());
  }

  /** إحصائيات عامة للعرض في الواجهة — بدون مصادقة (تستخدمها الصفحة الرئيسية SSR) */
  @Get("stats")
  stats() {
    return this.ai.passthrough("get", "/api/stats");
  }
}
