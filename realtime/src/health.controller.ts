import { Controller, Get } from "@nestjs/common";
import { AiProxyService } from "./chat/ai-proxy.service";

@Controller("health")
export class HealthController {
  constructor(private readonly ai: AiProxyService) {}

  @Get()
  async check() {
    const aiUp = await this.ai.healthy();
    return { status: "ok", service: "realtime", ai: aiUp ? "up" : "down" };
  }
}
