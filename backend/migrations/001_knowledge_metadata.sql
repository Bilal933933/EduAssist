ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS grade VARCHAR(32);
ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS stage VARCHAR(32);
ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS subject VARCHAR(128);
ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS branch VARCHAR(128);
ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS source_type VARCHAR(32);
ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS book_id VARCHAR(128);
ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS unit VARCHAR(255);
ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS lesson VARCHAR(255);
ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS concepts TEXT[];

CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_grade ON knowledge_chunks (grade);
CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_stage ON knowledge_chunks (stage);
CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_subject ON knowledge_chunks (subject);
CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_branch ON knowledge_chunks (branch);
CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_source_type ON knowledge_chunks (source_type);
CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_book_id ON knowledge_chunks (book_id);
CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_grade_subject ON knowledge_chunks (grade, subject);
CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_stage_subject ON knowledge_chunks (stage, subject);
CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_source_type_subject ON knowledge_chunks (source_type, subject);
