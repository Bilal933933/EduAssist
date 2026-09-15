import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  Index,
} from 'typeorm';

/**
 * Lesson Entity - جدول الدروس المحفوظة
 * يخزن الدروس التي يحفظها المعلم
 */

@Entity('lessons')
@Index('idx_lessons_teacher_id', ['teacherId'])
@Index('idx_lessons_topic', ['topic'])
@Index('idx_lessons_created_at', ['createdAt'])
export class LessonEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column('uuid')
  teacherId!: string; // معرف المعلم الحالي

  @Column('varchar', { length: 255 })
  title!: string; // عنوان الدرس

  @Column('text')
  content!: string; // محتوى الدرس

  @Column('varchar', { length: 100 })
  topic!: string; // "الفاعل", "النعت", إلخ

  @Column('varchar', { length: 50, nullable: true })
  grade!: string; // "أول ثانوي", "ثالث ثانوي"

  @Column('varchar', { length: 100, nullable: true })
  subject!: string; // "نحو", "صرف"

  @Column('uuid', { nullable: true })
  sourceMessageId!: string; // معرف الرسالة الأصلية من الدردشة

  @Column('text', { nullable: true })
  notes!: string; // الملاحظات الشخصية على الدرس

  @Column('boolean', { default: false })
  isPinned!: boolean; // هل الدرس مثبت

  @Column('simple-array', { default: () => `'{}'` })
  tags!: string[]; // ["مهم", "للاختبار"]

  @CreateDateColumn()
  createdAt!: Date;

  @UpdateDateColumn()
  updatedAt!: Date;
}
