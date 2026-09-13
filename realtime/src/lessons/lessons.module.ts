import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { LessonEntity } from '../database/entities/lesson.entity';
import { LessonRepository } from '../database/repositories/lesson.repository';
import { LessonsService } from './lessons.service';
import { LessonsController } from './lessons.controller';

@Module({
  imports: [TypeOrmModule.forFeature([LessonEntity])],
  controllers: [LessonsController],
  providers: [LessonsService, LessonRepository],
  exports: [LessonsService, LessonRepository],
})
export class LessonsModule {}
