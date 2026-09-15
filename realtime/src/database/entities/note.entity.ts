import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
  Unique,
} from 'typeorm';
import { LessonEntity } from './lesson.entity';

/**
 * Note Entity - جدول الملاحظات الشخصية
 * ملاحظة واحدة فقط لكل درس
 */

@Entity('lesson_notes')
@Unique(['lessonId'])
export class NoteEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column('uuid')
  lessonId!: string;

  @Column('uuid')
  teacherId!: string;

  @Column('text', { nullable: true })
  content!: string; // محتوى الملاحظة

  @Column('boolean', { default: false })
  isPinned!: boolean;

  @CreateDateColumn()
  createdAt!: Date;

  @UpdateDateColumn()
  updatedAt!: Date;

  // العلاقة مع Lesson
  @ManyToOne(() => LessonEntity, {
    onDelete: 'CASCADE',
  })
  @JoinColumn({ name: 'lessonId' })
  lesson!: LessonEntity;
}
