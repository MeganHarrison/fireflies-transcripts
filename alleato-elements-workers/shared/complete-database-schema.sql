-- Complete D1 Database Schema for RAG Pipeline
-- This schema supports the full functionality including project linking and insights

-- Projects table (new)
CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'on_hold', 'cancelled')),
  team_members TEXT, -- JSON array of team member emails/names
  keywords TEXT, -- JSON array of project-specific keywords
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Meetings table (existing, but needs project_id)
CREATE TABLE IF NOT EXISTS meetings (
  id TEXT PRIMARY KEY,
  fireflies_id TEXT UNIQUE NOT NULL,
  project_id TEXT, -- New field for project association
  title TEXT NOT NULL,
  date DATETIME NOT NULL,
  duration INTEGER NOT NULL,
  participants TEXT NOT NULL, -- JSON array
  summary TEXT,
  transcript_url TEXT,
  organizer_email TEXT,
  meeting_url TEXT,
  bucket_key TEXT,
  transcript_preview TEXT,
  vector_processed BOOLEAN DEFAULT FALSE,
  insight_generated BOOLEAN DEFAULT FALSE,
  project_confidence_score REAL, -- Confidence in project assignment (0-1)
  needs_project_review BOOLEAN DEFAULT FALSE, -- Flag for manual review
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Document chunks table (existing, add project_id)
CREATE TABLE IF NOT EXISTS meeting_chunks (
  id TEXT PRIMARY KEY,
  meeting_id TEXT NOT NULL,
  project_id TEXT, -- Inherited from meeting
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  speaker_info TEXT, -- JSON with speaker details
  start_time INTEGER, -- Timestamp in seconds
  end_time INTEGER, -- Timestamp in seconds
  embedding_id TEXT, -- Reference to Vectorize index
  metadata TEXT, -- Additional JSON metadata
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (meeting_id) REFERENCES meetings(id),
  FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Project insights table (new)
CREATE TABLE IF NOT EXISTS project_insights (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  meeting_id TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('general_info', 'positive_feedback', 'risks', 'action_items')),
  text TEXT NOT NULL,
  confidence_score REAL DEFAULT 0.8,
  extracted_entities TEXT, -- JSON array of entities (people, dates, etc.)
  is_verified BOOLEAN DEFAULT FALSE, -- User confirmation flag
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (meeting_id) REFERENCES meetings(id)
);

-- Meeting summaries table (new)
CREATE TABLE IF NOT EXISTS meeting_summaries (
  id TEXT PRIMARY KEY,
  meeting_id TEXT UNIQUE NOT NULL,
  project_id TEXT,
  summary_short TEXT, -- 2-3 sentences
  summary_medium TEXT, -- 1 paragraph
  summary_long TEXT, -- Detailed summary
  key_decisions TEXT, -- JSON array
  key_topics TEXT, -- JSON array
  sentiment_score REAL, -- Overall sentiment (-1 to 1)
  energy_level TEXT CHECK (energy_level IN ('low', 'medium', 'high')),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (meeting_id) REFERENCES meetings(id),
  FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Project tasks table (new)
CREATE TABLE IF NOT EXISTS project_tasks (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  meeting_id TEXT NOT NULL,
  insight_id TEXT, -- Link to source insight
  task_description TEXT NOT NULL,
  assignee TEXT, -- Email or name
  due_date DATE,
  priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
  completion_notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME,
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (meeting_id) REFERENCES meetings(id),
  FOREIGN KEY (insight_id) REFERENCES project_insights(id)
);

-- Project sentiment tracking (new)
CREATE TABLE IF NOT EXISTS project_sentiment (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  meeting_id TEXT NOT NULL,
  date DATE NOT NULL,
  sentiment_score REAL NOT NULL, -- -1 to 1
  confidence REAL DEFAULT 0.8,
  sample_quotes TEXT, -- JSON array of representative quotes
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (meeting_id) REFERENCES meetings(id)
);

-- AI chat sessions (existing)
CREATE TABLE IF NOT EXISTS ai_chat_sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  project_id TEXT, -- Add project context
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- AI chat messages (existing)
CREATE TABLE IF NOT EXISTS ai_chat_messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  relevant_chunks TEXT, -- JSON array of chunk IDs used
  feedback_score INTEGER CHECK (feedback_score IN (-1, 0, 1)), -- Thumbs down/neutral/up
  feedback_category TEXT, -- User categorization of response
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES ai_chat_sessions(id)
);

-- Processing queue (existing)
CREATE TABLE IF NOT EXISTS processing_queue (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  source_type TEXT NOT NULL,
  operation TEXT NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  priority INTEGER DEFAULT 5,
  error_message TEXT,
  retry_count INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  started_at DATETIME,
  completed_at DATETIME
);

-- Fireflies sync state (existing)
CREATE TABLE IF NOT EXISTS fireflies_sync_state (
  id TEXT PRIMARY KEY DEFAULT 'singleton',
  last_sync_timestamp DATETIME,
  last_successful_sync DATETIME,
  total_synced INTEGER DEFAULT 0,
  last_error TEXT,
  sync_cursor TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_meetings_fireflies_id ON meetings(fireflies_id);
CREATE INDEX IF NOT EXISTS idx_meetings_project_id ON meetings(project_id);
CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(date DESC);
CREATE INDEX IF NOT EXISTS idx_meetings_needs_review ON meetings(needs_project_review) WHERE needs_project_review = TRUE;

CREATE INDEX IF NOT EXISTS idx_chunks_meeting_id ON document_chunks(meeting_id);
CREATE INDEX IF NOT EXISTS idx_chunks_project_id ON document_chunks(project_id);

CREATE INDEX IF NOT EXISTS idx_insights_project_id ON project_insights(project_id);
CREATE INDEX IF NOT EXISTS idx_insights_meeting_id ON project_insights(meeting_id);
CREATE INDEX IF NOT EXISTS idx_insights_category ON project_insights(category);

CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON project_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON project_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON project_tasks(assignee);

CREATE INDEX IF NOT EXISTS idx_sentiment_project_date ON project_sentiment(project_id, date DESC);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON ai_chat_messages(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON ai_chat_sessions(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_project ON ai_chat_sessions(project_id);

CREATE INDEX IF NOT EXISTS idx_queue_status ON processing_queue(status, priority DESC);