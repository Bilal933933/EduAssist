import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  Index,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { LessonEntity } from './lesson.entity';

/**
 * Question Entity - جدول الأسئلة المولدة
 * الأسئلة التي يولدها الـ AI
 */

@Entity('generated_questions')
@Index('idx_teacher_id', ['teacherId'])
@Index('idx_lesson_id', ['lessonId'])
@Index('idx_difficulty', ['difficulty'])
export class QuestionEntity {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column('uuid', { nullable: true })
  lessonId: string; // معرف الدرس (اختياري)

  @Column('uuid')
  teacherId: string; // معرف المعلم

  @Column('text')
  questionText: string; // نص السؤال

  @Column('varchar', { length: 50 })
  type: 'multiple_choice' | 'essay' | 'true_false' | 'fill_blank';

  @Column('varchar', { length: 50 })
  difficulty: 'easy' | 'medium' | 'hard';

  @Column('varchar', { length: 100 })
  topic: string; // "الفاعل", "النعت", إلخ

  // الخيارات (JSON)
  // مثال: { "A": "الضمة", "B": "الفتحة", "C": "الكسرة", "D": "السكون" }
  @Column('jsonb', { nullable: true })
  options: Record<string, string>;

  @Column('text')
  correctAnswer: string; // "A" أو "الضمة"

  @Column('text')
  explanation: string; // شرح الإجابة الصحيحة

  @Column('boolean', { default: false })
  isUsed: boolean; // هل استُخدمت في اختبار

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  // العلاقة مع Lesson
  @ManyToOne(() => LessonEntity, {
    onDelete: 'CASCADE',
    nullable: true,
  })
  @JoinColumn({ name: 'lessonId' })
  lesson: LessonEntity;
}
