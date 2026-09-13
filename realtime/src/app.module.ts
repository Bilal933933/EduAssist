import { Module } from "@nestjs/common";
import { AuthController } from "./auth/auth.controller";
import { AiProxyService } from "./chat/ai-proxy.service";
import { ChatGateway } from "./chat/chat.gateway";
import { HealthController } from "./health.controller";
import { ProxyController } from "./gateway/proxy.controller";

@Module({
  controllers: [AuthController, HealthController, ProxyController],
  providers: [AiProxyService, ChatGateway],
})
export class AppModule {}
