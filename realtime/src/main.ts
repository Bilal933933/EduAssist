import "reflect-metadata";
import { NestFactory } from "@nestjs/core";
import { NextFunction, Request, Response } from "express";
import { AppModule } from "./app.module";
import { HttpExceptionFilter } from "./common/filters/http-exception.filter";
import { TransformInterceptor } from "./common/interceptors/transform.interceptor";
import { getLogger } from "./common/logger";
import { newRequestId, runWithRequestId } from "./common/request-context";
import { config } from "./config";
import { ensureSchema } from "./db";

async function bootstrap() {
  // فشل مغلق: لا تشغيل بدون أسرار معرفة
  if (!config.jwtSecret) {
    console.error("JWT_SECRET غير معرفة في .env — رفض التشغيل.");
    process.exit(1);
  }
  if (!config.internalApiKey) {
    console.error("INTERNAL_API_KEY غير معرفة في .env — رفض التشغيل.");
    process.exit(1);
  }

  await ensureSchema();

  const app = await NestFactory.create(AppModule, { bufferLogs: false });
  app.enableCors({ origin: true, exposedHeaders: ["X-Request-Id"] });

  // RequestId + access log — يطابق بايثون (request_id_middleware + access_log_middleware)
  const http = app.getHttpAdapter().getInstance();
  http.use((req: Request, res: Response, next: NextFunction) => {
    const rid = (req.headers["x-request-id"] as string) || newRequestId();
    res.setHeader("X-Request-Id", rid);
    const start = Date.now();
    res.on("finish", () => {
      runWithRequestId(rid, () => {
        getLogger("app").info(
          JSON.stringify({
            type: "access",
            method: req.method,
            path: req.path,
            status: res.statusCode,
            duration_ms: Date.now() - start,
          }),
        );
      });
    });
    runWithRequestId(rid, () => next());
  });

  // مغلف موحد للنجاح + هندلة موحدة للفشل (نفس بايثون)
  app.useGlobalInterceptors(new TransformInterceptor());
  app.useGlobalFilters(new HttpExceptionFilter());

  app.enableShutdownHooks();
  await app.listen(config.port);
  console.log(`Realtime Gateway يعمل على المنفذ ${config.port}`);
}

bootstrap().catch((err) => {
  console.error("فشل إقلاع Realtime:", (err as Error)?.message ?? err);
  process.exit(1);
});
