export interface Env {
  // Environment variables
  FIREFLIES_API_KEY: string;
  FIREFLIES_API_URL: string;
  
  // Bindings
  DB: D1Database;
  R2: R2Bucket;
  SYNC_STATE: KVNamespace;
  PROCESSING_QUEUE: Queue;
}

export interface FirefliesTranscript {
  id: string;
  title: string;
  date: string;
  duration: number;
  participants: string[];
  transcript_url?: string;
  summary?: string;
  sentences?: FirefliesSentence[];
  organizer_email?: string;
  meeting_url?: string;
  audio_url?: string;
  video_url?: string;
}

export interface FirefliesSentence {
  text: string;
  speaker_name: string;
  speaker_email?: string;
  start_time: number;
  end_time: number;
}

export interface SyncState {
  lastSyncTimestamp: string | null;
  lastSuccessfulSync: string | null;
  totalSynced: number;
  lastError: string | null;
  syncCursor: string | null;
}

export interface ProcessingTask {
  meetingId: string;
  operation: 'vectorize' | 'generate_insights' | 'extract_tasks' | 'summarize';
  priority: number;
  metadata?: Record<string, any>;
}