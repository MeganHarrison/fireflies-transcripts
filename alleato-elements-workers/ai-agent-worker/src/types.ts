import { Ai } from '@cloudflare/ai';

export interface Env {
  // Environment variables
  OPENAI_API_KEY?: string;
  
  // Bindings
  DB: D1Database;
  AI: Ai;
  VECTOR_INDEX: VectorizeIndex;
  CHAT_SESSIONS: KVNamespace;
  RESPONSE_CACHE: KVNamespace;
  ANALYTICS: AnalyticsEngineDataset;
}

export interface ChatRequest {
  query: string;
  projectId?: string;
  sessionId?: string;
  chatHistory?: ChatMessage[];
  mode?: 'recall' | 'strategy' | 'balanced';
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface RetrievedChunk {
  id: string;
  text: string;
  score: number;
  meetingId: string;
  projectId?: string;
  metadata?: Record<string, any>;
}

export interface ProjectContext {
  project?: {
    id: string;
    title: string;
    status: string;
    client?: string;
  };
  recentInsights: Array<{
    category: string;
    text: string;
    meetingDate: string;
  }>;
  activeTasks: Array<{
    description: string;
    assignedTo?: string;
    dueDate?: string;
    priority: string;
  }>;
  sentiment: {
    current: number;
    trend: 'improving' | 'stable' | 'declining';
  };
}

export interface ChatSession {
  id: string;
  projectId?: string;
  messages: ChatMessage[];
  context: ProjectContext;
  createdAt: string;
  updatedAt: string;
}

export interface VectorizeIndex {
  query(vector: number[], options: QueryOptions): Promise<VectorizeMatches>;
}

export interface QueryOptions {
  topK: number;
  filter?: Record<string, any>;
  returnMetadata?: boolean;
}

export interface VectorizeMatches {
  matches: Array<{
    id: string;
    score: number;
    metadata?: Record<string, any>;
  }>;
}

export interface AnalyticsEngineDataset {
  writeDataPoint(data: {
    blobs: string[];
    doubles: number[];
    indexes: string[];
  }): void;
}