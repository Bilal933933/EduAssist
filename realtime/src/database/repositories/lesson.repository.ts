import { Injectable } from '@nestjs/common';
import { DataSource, Repository } from 'typeorm';
import { LessonEntity } from '../entities/lesson.entity';

/**
 * LessonRepository - نمط Repository للدروس
 * يوفر واجهة موحدة للتعامل مع قاعدة البيانات
 */

@Injectable()
export class LessonRepository extends Repository<LessonEntity> {
  constructor(private dataSource: DataSource) {
    super(LessonEntity, dataSource.createEntityManager());
  }

  /**
   * الحصول على جميع دروس المعلم
   */
  async findByTeacherId(teacherId: string): Promise<LessonEntity[]> {
    return this.find({
      where: { teacherId },
      order: {
        isPinned: 'DESC', // المثبتة أولاً
        updatedAt: 'DESC',
      },
    });
  }

  /**
   * البحث عن دروس حسب الموضوع
   */
  async findByTopic(
    teacherId: string,
    topic: string
  ): Promise<LessonEntity[]> {
    return this.find({
      where: { teacherId, topic },
      order: { updatedAt: 'DESC' },
    });
  }

  /**
   * البحث عن دروس حسب الصف
   */
  async findByGrade(
    teacherId: string,
    grade: string
  ): Promise<LessonEntity[]> {
    return this.find({
      where: { teacherId, grade },
      order: { updatedAt: 'DESC' },
    });
  }

  /**
   * البحث النصي في الدروس
   */
  async search(
    teacherId: string,
    query: string
  ): Promise<LessonEntity[]> {
    return this.createQueryBuilder('lesson')
      .where('lesson.teacherId = :teacherId', { teacherId })
      .andWhere(
        '(lesson.title ILIKE :query OR lesson.content ILIKE :query OR lesson.topic ILIKE :query)',
        { query: `%${query}%` }
      )
      .orderBy('lesson.isPinned', 'DESC')
      .addOrderBy('lesson.updatedAt', 'DESC')
      .getMany();
  }

  /**
   * الحصول على الدروس المثبتة
   */
  async findPinned(teacherId: string): Promise<LessonEntity[]> {
    return this.find({
      where: { teacherId, isPinned: true },
      order: { updatedAt: 'DESC' },
    });
  }

  /**
   * الحصول على أحدث الدروس
   */
  async findRecent(teacherId: string, limit: number = 10): Promise<LessonEntity[]> {
    return this.find({
      where: { teacherId },
      order: { createdAt: 'DESC' },
      take: limit,
    });
  }

  /**
   * حذف درس مع علاقاته
   */
  async deleteWithRelations(id: string): Promise<void> {
    await this.delete(id);
  }

  /**
   * عد الدروس حسب الموضوع
   */
  async countByTopic(teacherId: string, topic: string): Promise<number> {
    return this.count({
      where: { teacherId, topic },
    });
  }

  /**
   * الحصول على جميع المواضيع الفريدة
   */
  async getUniquetopics(teacherId: string): Promise<string[]> {
    const results = await this.createQueryBuilder('lesson')
      .select('DISTINCT lesson.topic', 'topic')
      .where('lesson.teacherId = :teacherId', { teacherId })
      .getRawMany();

    return results.map(r => r.topic);
  }
}
