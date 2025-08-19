-- Shared database schema for all workers
-- This should be applied to the D1 database before deploying workers

-- Chat sessions table (missing from current schema)
CREATE TABLE IF NOT EXISTS ai_chat_sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Chat messages table (missing from current schema)  
CREATE TABLE IF NOT EXISTS ai_chat_messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES ai_chat_sessions(id)
);

-- Index for faster chat queries
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON ai_chat_messages(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON ai_chat_sessions(user_id, created_at);

-- Add indexes for existing tables if they don't exist
CREATE INDEX IF NOT EXISTS idx_meetings_fireflies_id ON meetings(fireflies_id);
CREATE INDEX IF NOT EXISTS idx_transcripts_meeting_id ON transcripts(meeting_id);
CREATE INDEX IF NOT EXISTS idx_transcript_chunks_meeting_id ON transcript_chunks(meeting_id);