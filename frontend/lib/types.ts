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

export interface StatsResponse {
  total_chunks: number;
  indexed: boolean;
}
