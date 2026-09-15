import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { AuthController } from "./auth/auth.controller";
import { AiProxyService } from "./chat/ai-proxy.service";
import { ChatGateway } from "./chat/chat.gateway";
import { HealthController } from "./health.controller";
import { ProxyController } from "./gateway/proxy.controller";
import { LessonsModule } from "./lessons/lessons.module";
import { LessonEntity } from "./database/entities/lesson.entity";
import { NoteEntity } from "./database/entities/note.entity";
import { QuestionEntity } from "./database/entities/question.entity";
import { config } from "./config";

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: "postgres",
      url: config.databaseUrl,
      entities: [LessonEntity, NoteEntity, QuestionEntity],
      // مدرس واحد، مرحلة تطوير: إنشاء تلقائي للجداول.
      // قبل أي توسع SaaS: synchronize:false + تشغيل migrations مُدارة.
      synchronize: true,
    }),
    LessonsModule,
  ],
  controllers: [AuthController, HealthController, ProxyController],
  providers: [AiProxyService, ChatGateway],
})
export class AppModule {}
