import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { LessonRepository } from '../database/repositories/lesson.repository';
import { LessonEntity } from '../database/entities/lesson.entity';
import { CreateLessonDto, UpdateLessonDto, SearchLessonsDto } from './dto';

/**
 * LessonsService - خدمة إدارة الدروس
 * يتعامل مع منطق الأعمال المتعلق بالدروس
 */

@Injectable()
export class LessonsService {
  constructor(private readonly lessonRepository: LessonRepository) {}

  /**
   * إنشاء درس جديد
   */
  async create(
    teacherId: string,
    createLessonDto: CreateLessonDto
  ): Promise<LessonEntity> {
    // التحقق من البيانات
    if (!createLessonDto.title || !createLessonDto.content) {
      throw new BadRequestException(
        'العنوان والمحتوى مطلوبان'
      );
    }

    const lesson = this.lessonRepository.create({
      teacherId,
      ...createLessonDto,
    });

    return this.lessonRepository.save(lesson);
  }

  /**
   * الحصول على جميع دروس المعلم
   */
  async findAll(teacherId: string): Promise<LessonEntity[]> {
    return this.lessonRepository.findByTeacherId(teacherId);
  }

  /**
   * الحصول على درس واحد
   */
  async findOne(id: string, teacherId: string): Promise<LessonEntity> {
    const lesson = await this.lessonRepository.findOne({
      where: { id, teacherId },
    });

    if (!lesson) {
      throw new NotFoundException('الدرس غير موجود');
    }

    return lesson;
  }

  /**
   * تحديث درس
   */
  async update(
    id: string,
    teacherId: string,
    updateLessonDto: UpdateLessonDto
  ): Promise<LessonEntity> {
    const lesson = await this.findOne(id, teacherId);

    Object.assign(lesson, updateLessonDto);

    return this.lessonRepository.save(lesson);
  }

  /**
   * تحديث الملاحظات على درس
   */
  async updateNotes(
    id: string,
    teacherId: string,
    notes: string
  ): Promise<LessonEntity> {
    const lesson = await this.findOne(id, teacherId);
    lesson.notes = notes;
    return this.lessonRepository.save(lesson);
  }

  /**
   * تثبيت/فك تثبيت درس
   */
  async togglePin(
    id: string,
    teacherId: string
  ): Promise<LessonEntity> {
    const lesson = await this.findOne(id, teacherId);
    lesson.isPinned = !lesson.isPinned;
    return this.lessonRepository.save(lesson);
  }

  /**
   * حذف درس
   */
  async delete(id: string, teacherId: string): Promise<void> {
    const lesson = await this.findOne(id, teacherId);
    await this.lessonRepository.delete(lesson.id);
  }

  /**
   * البحث في الدروس
   */
  async search(
    teacherId: string,
    searchLessonsDto: SearchLessonsDto
  ): Promise<LessonEntity[]> {
    const { query, topic, grade } = searchLessonsDto;

    if (query) {
      return this.lessonRepository.search(teacherId, query);
    }

    if (topic) {
      return this.lessonRepository.findByTopic(teacherId, topic);
    }

    if (grade) {
      return this.lessonRepository.findByGrade(teacherId, grade);
    }

    return this.lessonRepository.findByTeacherId(teacherId);
  }

  /**
   * الحصول على الدروس المثبتة
   */
  async getPinned(teacherId: string): Promise<LessonEntity[]> {
    return this.lessonRepository.findPinned(teacherId);
  }

  /**
   * الحصول على أحدث الدروس
   */
  async getRecent(teacherId: string, limit: number = 10): Promise<LessonEntity[]> {
    return this.lessonRepository.findRecent(teacherId, limit);
  }

  /**
   * الحصول على الإحصائيات
   */
  async getStatistics(teacherId: string): Promise<{
    totalLessons: number;
    topics: string[];
    pinnedCount: number;
  }> {
    const lessons = await this.lessonRepository.findByTeacherId(teacherId);
    const topics = await this.lessonRepository.getUniquetopics(teacherId);
    const pinnedCount = lessons.filter(l => l.isPinned).length;

    return {
      totalLessons: lessons.length,
      topics,
      pinnedCount,
    };
  }
}
