import { Injectable } from '@nestjs/common';
import { DataSource, Repository } from 'typeorm';
import { QuestionEntity } from '../entities/question.entity';

/**
 * QuestionRepository - نمط Repository للأسئلة
 */

@Injectable()
export class QuestionRepository extends Repository<QuestionEntity> {
  constructor(private dataSource: DataSource) {
    super(QuestionEntity, dataSource.createEntityManager());
  }

  /**
   * الحصول على الأسئلة حسب الدرس
   */
  async findByLessonId(lessonId: string): Promise<QuestionEntity[]> {
    return this.find({
      where: { lessonId },
      order: { createdAt: 'DESC' },
    });
  }

  /**
   * الحصول على الأسئلة حسب المعلم
   */
  async findByTeacherId(teacherId: string): Promise<QuestionEntity[]> {
    return this.find({
      where: { teacherId },
      order: { createdAt: 'DESC' },
    });
  }

  /**
   * الحصول على الأسئلة حسب مستوى الصعوبة
   */
  async findByDifficulty(
    teacherId: string,
    difficulty: 'easy' | 'medium' | 'hard'
  ): Promise<QuestionEntity[]> {
    return this.find({
      where: { teacherId, difficulty },
      order: { createdAt: 'DESC' },
    });
  }

  /**
   * الحصول على الأسئلة حسب الموضوع
   */
  async findByTopic(teacherId: string, topic: string): Promise<QuestionEntity[]> {
    return this.find({
      where: { teacherId, topic },
      order: { createdAt: 'DESC' },
    });
  }

  /**
   * الحصول على الأسئلة المستخدمة
   */
  async findUsed(teacherId: string): Promise<QuestionEntity[]> {
    return this.find({
      where: { teacherId, isUsed: true },
      order: { createdAt: 'DESC' },
    });
  }

  /**
   * الحصول على الأسئلة غير المستخدمة
   */
  async findUnused(teacherId: string): Promise<QuestionEntity[]> {
    return this.find({
      where: { teacherId, isUsed: false },
      order: { createdAt: 'DESC' },
    });
  }

  /**
   * تسجيل السؤال كـ مستخدم
   */
  async markAsUsed(id: string): Promise<void> {
    await this.update(id, { isUsed: true });
  }

  /**
   * عد الأسئلة حسب المعلم
   */
  async countByTeacher(teacherId: string): Promise<number> {
    return this.count({ where: { teacherId } });
  }

  /**
   * عد الأسئلة المستخدمة
   */
  async countUsed(teacherId: string): Promise<number> {
    return this.count({ where: { teacherId, isUsed: true } });
  }

  /**
   * الحصول على الأسئلة من نطاق معين
   */
  async findByLessonAndDifficulty(
    lessonId: string,
    difficulty: 'easy' | 'medium' | 'hard'
  ): Promise<QuestionEntity[]> {
    return this.find({
      where: { lessonId, difficulty },
      order: { createdAt: 'DESC' },
    });
  }
}
