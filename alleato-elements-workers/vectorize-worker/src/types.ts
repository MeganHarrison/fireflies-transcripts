import { Ai } from '@cloudflare/ai';

export interface Env {
  // Bindings
  DB: D1Database;
  R2: R2Bucket;
  AI: Ai;
  VECTOR_INDEX: VectorizeIndex;
}

export interface ProcessingMessage {
  meetingId: string;
  operation: 'vectorize' | 'generate_insights' | 'extract_tasks' | 'summarize';
  priority: number;
  metadata?: Record<string, any>;
}

export interface Meeting {
  id: string;
  fireflies_id: string;
  title: string;
  date: string;
  participants: string;
  summary?: string;
  r2_key?: string;
  project?: string;
}

export interface TranscriptSentence {
  text: string;
  speaker_name: string;
  speaker_email?: string;
  start_time: number;
  end_time: number;
}

export interface TextChunk {
  text: string;
  startTime: number;
  endTime: number;
  speakers: Set<string>;
  sentenceCount: number;
}

export interface ProjectMatch {
  projectId: string;
  confidence: number;
  reasons: string[];
}

export interface VectorizeIndex {
  insert(vectors: VectorizeVector[]): Promise<{ ids: string[] }>;
  query(vector: number[], options: QueryOptions): Promise<VectorizeMatches>;
  deleteByIds(ids: string[]): Promise<void>;
}

export interface VectorizeVector {
  id: string;
  values: number[];
  metadata?: Record<string, any>;
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