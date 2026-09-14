export interface KnowledgeHit {
  title: string;
  text: string;
  source: string;
  page: number | null;
  similarity: number;
}

export interface AgentTraceStep {
  label: string;
  detail?: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  role: "user" | "assistant";
  createdAt: Date;
  hits?: KnowledgeHit[];
  trace?: AgentTraceStep[];
  durationMs?: number;
  streaming?: boolean;
}

export interface ChatResponse {
  answer: string;
  hits: KnowledgeHit[];
  thread_id: number | null;
}

export interface ChatThread {
  id: number;
  title: string;
  message_count: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface StoredMessage {
  id: number;
  thread_id: number;
  role: "user" | "assistant";
  content: string;
  sources: KnowledgeHit[] | null;
  created_at: string | null;
}

export interface SubjectCount {
  subject: string;
  stage: string | null;
  chunks: number;
}

export interface Flashcard {
  q: string;
  a: string;
}

export interface QuizQuestion {
  q: string;
  options: string[];
  answer: number;
  explain?: string;
}

export interface StatsResponse {
  total_chunks: number;
  indexed: boolean;
  by_subject?: SubjectCount[];
}

export interface TeacherTopic {
  topic: string;
  count: number;
  grade_id: number | null;
}

export interface TeacherLessonEvent {
  topic: string;
  grade: string | null;
  grade_id: number | null;
  at: string | null;
  event_type: string | null;
}

export interface TeacherProfile {
  teacher_id: string;
  display_name: string;
  preferred_grades: string[];
  frequent_topics: TeacherTopic[];
  interaction_count: number;
  recent_lessons: TeacherLessonEvent[];
  common_mistakes: { id: number; mistake: string; topic: string | null; count: number }[];
  summary: string;
  class_context: string;
  updated_at: string | null;
}

export interface MemoryResponse {
  profile: TeacherProfile;
  prompt_block: string;
  mistakes_for_grade: unknown[];
  recent_for_grade: unknown[];
  filter_grade: string | null;
}
