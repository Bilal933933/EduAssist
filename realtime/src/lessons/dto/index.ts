import { IsString, IsOptional, IsArray, IsUUID } from 'class-validator';

/**
 * CreateLessonDto - بيانات إنشاء درس جديد
 */
export class CreateLessonDto {
  @IsString()
  title: string;

  @IsString()
  content: string;

  @IsString()
  topic: string;

  @IsOptional()
  @IsString()
  grade?: string;

  @IsOptional()
  @IsString()
  subject?: string;

  @IsOptional()
  @IsUUID()
  sourceMessageId?: string;

  @IsOptional()
  @IsArray()
  tags?: string[];
}

/**
 * UpdateLessonDto - بيانات تحديث درس
 */
export class UpdateLessonDto {
  @IsOptional()
  @IsString()
  title?: string;

  @IsOptional()
  @IsString()
  content?: string;

  @IsOptional()
  @IsString()
  topic?: string;

  @IsOptional()
  @IsString()
  grade?: string;

  @IsOptional()
  @IsString()
  subject?: string;

  @IsOptional()
  @IsArray()
  tags?: string[];
}

/**
 * SearchLessonsDto - بيانات البحث في الدروس
 */
export class SearchLessonsDto {
  @IsOptional()
  @IsString()
  query?: string;

  @IsOptional()
  @IsString()
  topic?: string;

  @IsOptional()
  @IsString()
  grade?: string;
}

/**
 * UpdateNotesDto - بيانات تحديث الملاحظات
 */
export class UpdateNotesDto {
  @IsOptional()
  @IsString()
  notes?: string;
}
