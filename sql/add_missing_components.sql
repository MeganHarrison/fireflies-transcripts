-- Add missing components to existing Supabase schema
-- Run this in Supabase SQL Editor if you're missing the vector search function

-- Enable vector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create or replace the vector search function
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

-- Grant permissions
GRANT EXECUTE ON FUNCTION search_chunks TO authenticated;
GRANT EXECUTE ON FUNCTION search_chunks TO service_role;

-- Verify the function was created
SELECT 'Vector search function created successfully!' as message;