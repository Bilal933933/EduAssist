import { MigrationInterface, QueryRunner, Table, TableIndex, TableForeignKey } from 'typeorm';

/**
 * Migration: إنشاء جداول الدروس والملاحظات والأسئلة
 * تاريخ: 2024-08-30
 */
export class CreateLessonsTablesNotesQuestionsAndIndices1693555200000
  implements MigrationInterface
{
  public async up(queryRunner: QueryRunner): Promise<void> {
    // 1. جدول الدروس
    await queryRunner.createTable(
      new Table({
        name: 'lessons',
        columns: [
          {
            name: 'id',
            type: 'uuid',
            isPrimary: true,
            generationStrategy: 'uuid',
            default: 'gen_random_uuid()',
          },
          {
            name: 'teacherId',
            type: 'uuid',
            isNullable: false,
          },
          {
            name: 'title',
            type: 'varchar',
            length: '255',
            isNullable: false,
          },
          {
            name: 'content',
            type: 'text',
            isNullable: false,
          },
          {
            name: 'topic',
            type: 'varchar',
            length: '100',
            isNullable: false,
          },
          {
            name: 'grade',
            type: 'varchar',
            length: '50',
            isNullable: true,
          },
          {
            name: 'subject',
            type: 'varchar',
            length: '100',
            isNullable: true,
          },
          {
            name: 'sourceMessageId',
            type: 'uuid',
            isNullable: true,
          },
          {
            name: 'notes',
            type: 'text',
            isNullable: true,
          },
          {
            name: 'isPinned',
            type: 'boolean',
            default: false,
          },
          {
            name: 'tags',
            type: 'simple-array',
            isNullable: true,
            default: `'{}'`,
          },
          {
            name: 'createdAt',
            type: 'timestamp',
            default: 'CURRENT_TIMESTAMP',
          },
          {
            name: 'updatedAt',
            type: 'timestamp',
            default: 'CURRENT_TIMESTAMP',
            onUpdate: 'CURRENT_TIMESTAMP',
          },
        ],
      }),
      true
    );

    // إضافة الفهارس للجدول lessons
    await queryRunner.createIndex(
      'lessons',
      new TableIndex({
        name: 'idx_lessons_teacher_id',
        columnNames: ['teacherId'],
      })
    );

    await queryRunner.createIndex(
      'lessons',
      new TableIndex({
        name: 'idx_lessons_topic',
        columnNames: ['topic'],
      })
    );

    await queryRunner.createIndex(
      'lessons',
      new TableIndex({
        name: 'idx_lessons_created_at',
        columnNames: ['createdAt'],
        isUnique: false,
        sort: 'DESC',
      })
    );

    // 2. جدول الملاحظات
    await queryRunner.createTable(
      new Table({
        name: 'lesson_notes',
        columns: [
          {
            name: 'id',
            type: 'uuid',
            isPrimary: true,
            generationStrategy: 'uuid',
            default: 'gen_random_uuid()',
          },
          {
            name: 'lessonId',
            type: 'uuid',
            isNullable: false,
          },
          {
            name: 'teacherId',
            type: 'uuid',
            isNullable: false,
          },
          {
            name: 'content',
            type: 'text',
            isNullable: true,
          },
          {
            name: 'isPinned',
            type: 'boolean',
            default: false,
          },
          {
            name: 'createdAt',
            type: 'timestamp',
            default: 'CURRENT_TIMESTAMP',
          },
          {
            name: 'updatedAt',
            type: 'timestamp',
            default: 'CURRENT_TIMESTAMP',
            onUpdate: 'CURRENT_TIMESTAMP',
          },
        ],
        uniques: [
          {
            name: 'unique_lesson_note',
            columnNames: ['lessonId'],
          },
        ],
      }),
      true
    );

    // إضافة الـ Foreign Key للملاحظات
    await queryRunner.createForeignKey(
      'lesson_notes',
      new TableForeignKey({
        columnNames: ['lessonId'],
        referencedColumnNames: ['id'],
        referencedTableName: 'lessons',
        onDelete: 'CASCADE',
      })
    );

    // 3. جدول الأسئلة
    await queryRunner.createTable(
      new Table({
        name: 'generated_questions',
        columns: [
          {
            name: 'id',
            type: 'uuid',
            isPrimary: true,
            generationStrategy: 'uuid',
            default: 'gen_random_uuid()',
          },
          {
            name: 'lessonId',
            type: 'uuid',
            isNullable: true,
          },
          {
            name: 'teacherId',
            type: 'uuid',
            isNullable: false,
          },
          {
            name: 'questionText',
            type: 'text',
            isNullable: false,
          },
          {
            name: 'type',
            type: 'varchar',
            length: '50',
            isNullable: false,
          },
          {
            name: 'difficulty',
            type: 'varchar',
            length: '50',
            isNullable: false,
          },
          {
            name: 'topic',
            type: 'varchar',
            length: '100',
            isNullable: false,
          },
          {
            name: 'options',
            type: 'jsonb',
            isNullable: true,
          },
          {
            name: 'correctAnswer',
            type: 'text',
            isNullable: false,
          },
          {
            name: 'explanation',
            type: 'text',
            isNullable: false,
          },
          {
            name: 'isUsed',
            type: 'boolean',
            default: false,
          },
          {
            name: 'createdAt',
            type: 'timestamp',
            default: 'CURRENT_TIMESTAMP',
          },
          {
            name: 'updatedAt',
            type: 'timestamp',
            default: 'CURRENT_TIMESTAMP',
            onUpdate: 'CURRENT_TIMESTAMP',
          },
        ],
      }),
      true
    );

    // إضافة الفهارس للجدول generated_questions
    await queryRunner.createIndex(
      'generated_questions',
      new TableIndex({
        name: 'idx_questions_teacher_id',
        columnNames: ['teacherId'],
      })
    );

    await queryRunner.createIndex(
      'generated_questions',
      new TableIndex({
        name: 'idx_questions_lesson_id',
        columnNames: ['lessonId'],
      })
    );

    await queryRunner.createIndex(
      'generated_questions',
      new TableIndex({
        name: 'idx_questions_difficulty',
        columnNames: ['difficulty'],
      })
    );

    // إضافة الـ Foreign Key للأسئلة
    await queryRunner.createForeignKey(
      'generated_questions',
      new TableForeignKey({
        columnNames: ['lessonId'],
        referencedColumnNames: ['id'],
        referencedTableName: 'lessons',
        onDelete: 'CASCADE',
      })
    );
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    // حذف الـ Foreign Keys
    await queryRunner.dropForeignKey('lesson_notes', 'unique_lesson_note');
    await queryRunner.dropForeignKey('generated_questions', 'idx_questions_lesson_id');

    // حذف الجداول
    await queryRunner.dropTable('generated_questions');
    await queryRunner.dropTable('lesson_notes');
    await queryRunner.dropTable('lessons');
  }
}
