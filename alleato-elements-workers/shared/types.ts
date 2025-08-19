// Shared types across all workers

export interface Meeting {
  id: string;
  title: string;
  date: string;
  duration: number;
  participants: string[];
  transcript?: string;
  summary?: string;
  project_id?: string;
  fireflies_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Transcript {
  id: string;
  meeting_id: string;
  content: string;
  speaker?: string;
  timestamp?: number;
  confidence?: number;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface ChatSession {
  id: string;
  user_id?: string;
  created_at: string;
  updated_at: string;
}

export interface EmbeddingChunk {
  id: string;
  meeting_id: string;
  content: string;
  embedding?: number[];
  metadata?: Record<string, any>;
  chunk_index: number;
}

export interface WorkerEnv {
  // D1 Database
  DB: D1Database;
  
  // Vectorize
  VECTORIZE: VectorizeIndex;
  
  // R2 Storage
  R2: R2Bucket;
  
  // KV Namespaces
  KV: KVNamespace;
  
  // Queue
  TRANSCRIPT_QUEUE: Queue;
  
  // Environment Variables
  OPENAI_API_KEY: string;
  FIREFLIES_API_KEY: string;
  AI_AGENT_WORKER_URL?: string;
  VECTORIZE_WORKER_URL?: string;
}

export interface QueueMessage {
  type: 'transcript_processing';
  meeting_id: string;
  transcript_content: string;
  metadata?: Record<string, any>;
}

export interface RAGResponse {
  response: string;
  sources?: Array<{
    id: string;
    content: string;
    metadata: Record<string, any>;
    score: number;
  }>;
  reasoning?: string;
}