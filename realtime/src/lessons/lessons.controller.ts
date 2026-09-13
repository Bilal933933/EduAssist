import {
  Controller,
  Get,
  Post,
  Patch,
  Delete,
  Body,
  Param,
  Query,
  HttpCode,
  HttpStatus,
  UseGuards,
} from '@nestjs/common';
import { LessonsService } from './lessons.service';
import {
  CreateLessonDto,
  UpdateLessonDto,
  SearchLessonsDto,
  UpdateNotesDto,
} from './dto';

/**
 * LessonsController - واجهة API للدروس
 */

@Controller('api/lessons')
export class LessonsController {
  constructor(private readonly lessonsService: LessonsService) {}

  /**
   * POST /api/lessons
   * إنشاء درس جديد
   */
  @Post()
  @HttpCode(HttpStatus.CREATED)
  async create(
    @Body() createLessonDto: CreateLessonDto
  ) {
    // معرف المعلم يأتي من JWT token (سيتم إضافته لاحقاً)
    const teacherId = 'temp-teacher-id'; // TODO: extract from JWT

    return this.lessonsService.create(teacherId, createLessonDto);
  }

  /**
   * GET /api/lessons
   * الحصول على جميع دروس المعلم
   */
  @Get()
  async findAll() {
    const teacherId = 'temp-teacher-id'; // TODO: extract from JWT
    return this.lessonsService.findAll(teacherId);
  }

  /**
   * GET /api/lessons/pinned
   * الحصول على الدروس المثبتة
   */
  @Get('pinned')
  async getPinned() {
    const teacherId = 'temp-teacher-id'; // TODO: extract from JWT
    return this.lessonsService.getPinned(teacherId);
  }

  /**
   * GET /api/lessons/recent
   * الحصول على أحدث الدروس
   */
  @Get('recent')
  async getRecent(@Query('limit') limit: number = 10) {
    const teacherId = 'temp-teacher-id'; // TODO: extract from JWT
    return this.lessonsService.getRecent(teacherId, limit);
  }

  /**
   * GET /api/lessons/search
   * البحث في الدروس
   */
  @Get('search')
  async search(
    @Query() searchLessonsDto: SearchLessonsDto
  ) {
    const teacherId = 'temp-teacher-id'; // TODO: extract from JWT
    return this.lessonsService.search(teacherId, searchLessonsDto);
  }

  /**
   * GET /api/lessons/statistics
   * الحصول على الإحصائيات
   */
  @Get('statistics')
  async getStatistics() {
    const teacherId = 'temp-teacher-id'; // TODO: extract from JWT
    return this.lessonsService.getStatistics(teacherId);
  }

  /**
   * GET /api/lessons/:id
   * الحصول على درس واحد
   */
  @Get(':id')
  async findOne(@Param('id') id: string) {
    const teacherId = 'temp-teacher-id'; // TODO: extract from JWT
    return this.lessonsService.findOne(id, teacherId);
  }

  /**
   * PATCH /api/lessons/:id
   * تحديث درس
   */
  @Patch(':id')
  async update(
    @Param('id') id: string,
    @Body() updateLessonDto: UpdateLessonDto
  ) {
    const teacherId = 'temp-teacher-id'; // TODO: extract from JWT
    return this.lessonsService.update(id, teacherId, updateLessonDto);
  }

  /**
   * PATCH /api/lessons/:id/notes
   * تحديث الملاحظات على درس
   */
  @Patch(':id/notes')
  async updateNotes(
    @Param('id') id: string,
    @Body() updateNotesDto: UpdateNotesDto
  ) {
    const teacherId = 'temp-teacher-id'; // TODO: extract from JWT
    return this.lessonsService.updateNotes(
      id,
      teacherId,
      updateNotesDto.notes || ''
    );
  }

  /**
   * PATCH /api/lessons/:id/pin
   * تثبيت/فك تثبيت درس
   */
  @Patch(':id/pin')
  async togglePin(@Param('id') id: string) {
    const teacherId = 'temp-teacher-id'; // TODO: extract from JWT
    return this.lessonsService.togglePin(id, teacherId);
  }

  /**
   * DELETE /api/lessons/:id
   * حذف درس
   */
  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  async delete(@Param('id') id: string) {
    const teacherId = 'temp-teacher-id'; // TODO: extract from JWT
    await this.lessonsService.delete(id, teacherId);
  }
}
