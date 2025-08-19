-- Supabase Schema for Fireflies RAG Pipeline
-- This schema supports the complete pipeline: ingest, vectorize, chat, and insights generation

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search optimization

-- Projects table to organize all meetings and insights
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    team_members TEXT[], -- Array of team member names/emails
    keywords TEXT[], -- Keywords for automatic project matching
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived', 'completed')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Meetings table to store transcript metadata
CREATE TABLE IF NOT EXISTS meetings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fireflies_transcript_id TEXT UNIQUE NOT NULL, -- Fireflies unique ID
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    meeting_date TIMESTAMPTZ NOT NULL,
    duration_seconds INTEGER,
    participants JSONB, -- Array of participant objects with name, email, etc.
    storage_bucket_path TEXT, -- Path to raw transcript in Supabase storage
    confidence_score REAL DEFAULT 0.0, -- Confidence in project assignment (0-1)
    needs_review BOOLEAN DEFAULT FALSE, -- Flag for human review of project assignment
    raw_metadata JSONB, -- Store complete Fireflies metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Meeting chunks table for vectorized content
CREATE TABLE IF NOT EXISTS meeting_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI ada-002 embeddings
    speaker_info JSONB, -- Speaker details for this chunk
    start_timestamp INTEGER, -- Start time in seconds
    end_timestamp INTEGER, -- End time in seconds
    metadata JSONB, -- Additional metadata (topics, entities, etc.)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(meeting_id, chunk_index)
);

-- Meeting summaries table
CREATE TABLE IF NOT EXISTS meeting_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    summary_type TEXT NOT NULL CHECK (summary_type IN ('short', 'medium', 'long')),
    content TEXT NOT NULL,
    key_points TEXT[], -- Array of key discussion points
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(meeting_id, summary_type)
);

-- Project insights table for categorized insights
CREATE TABLE IF NOT EXISTS project_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    category TEXT NOT NULL CHECK (category IN ('general_info', 'positive_feedback', 'risks', 'action_items')),
    text TEXT NOT NULL,
    confidence_score REAL DEFAULT 0.0 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    user_validated BOOLEAN DEFAULT FALSE,
    metadata JSONB, -- Additional context (speaker, timestamp, etc.)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project tasks table for extracted action items
CREATE TABLE IF NOT EXISTS project_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    insight_id UUID REFERENCES project_insights(id) ON DELETE SET NULL,
    task_description TEXT NOT NULL,
    assigned_to TEXT,
    due_date DATE,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    source_text TEXT, -- Original text that generated this task
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sentiment analysis table
CREATE TABLE IF NOT EXISTS sentiment_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID REFERENCES meetings(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    analysis_level TEXT NOT NULL CHECK (analysis_level IN ('meeting', 'project', 'speaker')),
    entity_id TEXT, -- Speaker ID if analysis_level is 'speaker'
    sentiment_score REAL NOT NULL CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    positive_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    negative_count INTEGER DEFAULT 0,
    analysis_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(meeting_id, analysis_level, entity_id, analysis_date)
);

-- User feedback table for continuous improvement
CREATE TABLE IF NOT EXISTS user_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    feedback_type TEXT NOT NULL CHECK (feedback_type IN ('chat_response', 'project_assignment', 'insight', 'task_extraction')),
    entity_id UUID NOT NULL, -- ID of the entity being rated (chunk, insight, task, etc.)
    rating TEXT CHECK (rating IN ('positive', 'negative', 'neutral')),
    comment TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    metadata JSONB
);

-- Chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    chunks_used UUID[], -- Array of chunk IDs used to generate response
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sync status table to track Fireflies sync progress
CREATE TABLE IF NOT EXISTS sync_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sync_type TEXT NOT NULL DEFAULT 'fireflies',
    last_sync_at TIMESTAMPTZ,
    last_successful_sync_at TIMESTAMPTZ,
    status TEXT DEFAULT 'idle' CHECK (status IN ('idle', 'running', 'failed', 'completed')),
    error_message TEXT,
    metadata JSONB, -- Store last processed ID, count, etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for optimal performance
CREATE INDEX IF NOT EXISTS idx_meetings_project_id ON meetings(project_id);
CREATE INDEX IF NOT EXISTS idx_meetings_fireflies_id ON meetings(fireflies_transcript_id);
CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(meeting_date DESC);
CREATE INDEX IF NOT EXISTS idx_meetings_needs_review ON meetings(needs_review) WHERE needs_review = TRUE;

CREATE INDEX IF NOT EXISTS idx_chunks_meeting_id ON meeting_chunks(meeting_id);
CREATE INDEX IF NOT EXISTS idx_chunks_project_id ON meeting_chunks(project_id);
CREATE INDEX IF NOT EXISTS idx_chunks_content_trgm ON meeting_chunks USING gin(content gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_insights_project_id ON project_insights(project_id);
CREATE INDEX IF NOT EXISTS idx_insights_meeting_id ON project_insights(meeting_id);
CREATE INDEX IF NOT EXISTS idx_insights_category ON project_insights(category);
CREATE INDEX IF NOT EXISTS idx_insights_confidence ON project_insights(confidence_score) WHERE confidence_score > 0.7;

CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON project_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON project_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON project_tasks(due_date) WHERE status != 'completed';

CREATE INDEX IF NOT EXISTS idx_sentiment_project_date ON sentiment_analysis(project_id, analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_entity ON user_feedback(entity_id, feedback_type);

-- Create vector similarity search index
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON meeting_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meetings_updated_at BEFORE UPDATE ON meetings
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_summaries_updated_at BEFORE UPDATE ON meeting_summaries
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_insights_updated_at BEFORE UPDATE ON project_insights
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON project_tasks
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sync_status_updated_at BEFORE UPDATE ON sync_status
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function for vector similarity search
CREATE OR REPLACE FUNCTION search_chunks(
    query_embedding vector(1536),
    match_count INT DEFAULT 10,
    filter_project_id UUID DEFAULT NULL
)
RETURNS TABLE (
    chunk_id UUID,
    meeting_id UUID,
    project_id UUID,
    content TEXT,
    similarity FLOAT,
    metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mc.id AS chunk_id,
        mc.meeting_id,
        mc.project_id,
        mc.content,
        1 - (mc.embedding <=> query_embedding) AS similarity,
        mc.metadata
    FROM meeting_chunks mc
    WHERE (filter_project_id IS NULL OR mc.project_id = filter_project_id)
        AND mc.embedding IS NOT NULL
    ORDER BY mc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Row Level Security (RLS) Policies
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (customize based on your auth strategy)
-- Example: Allow authenticated users to read all data but write only their own
CREATE POLICY "Enable read access for authenticated users" ON projects
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON meetings
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON meeting_chunks
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON project_insights
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON project_tasks
    FOR SELECT USING (auth.role() = 'authenticated');

-- Service role bypass for workers
CREATE POLICY "Service role has full access" ON projects
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access" ON meetings
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access" ON meeting_chunks
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access" ON meeting_summaries
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access" ON project_insights
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access" ON project_tasks
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access" ON sentiment_analysis
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access" ON sync_status
    FOR ALL USING (auth.role() = 'service_role');

-- Grant permissions for functions
GRANT EXECUTE ON FUNCTION search_chunks TO authenticated;
GRANT EXECUTE ON FUNCTION search_chunks TO service_role;