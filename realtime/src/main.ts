import "reflect-metadata";
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";
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

  const app = await NestFactory.create(AppModule);
  app.enableCors({ origin: true });
  await app.listen(config.port);
  console.log(`Realtime Gateway يعمل على المنفذ ${config.port}`);
}

bootstrap();
