# Supabase Implementation Guide

## Step 1: Execute the Schema

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Copy the entire contents of `supabase_schema.sql`
4. Paste and execute in the SQL Editor
5. Verify all tables were created successfully

## Step 2: Set up Storage Bucket

Create a storage bucket for raw transcripts:

```sql
-- Run this in SQL Editor
INSERT INTO storage.buckets (id, name, public)
VALUES ('fireflies-transcripts', 'fireflies-transcripts', false);
```

## Step 3: Configure Environment Variables

Update your `.env` file with these Supabase-specific variables:

```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key
```

## Step 4: Update Existing Code

Your existing `fireflies_webhook_pipeline.py` needs minor updates to work with the new schema:

1. Update the table name from `meeting_chunks` to match the new schema
2. Add project linking logic
3. Include the new metadata fields

## Step 5: Test the Implementation

```python
# Test script to verify setup
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

# Test creating a project
project = supabase.table('projects').insert({
    "name": "Test Project",
    "description": "Testing the schema",
    "team_members": ["user1@example.com", "user2@example.com"],
    "keywords": ["test", "demo"]
}).execute()

print("Project created:", project.data)
```

## Step 6: Enable Realtime (Optional)

If you want real-time updates:

```sql
-- Enable realtime for specific tables
ALTER PUBLICATION supabase_realtime ADD TABLE meetings;
ALTER PUBLICATION supabase_realtime ADD TABLE project_insights;
ALTER PUBLICATION supabase_realtime ADD TABLE project_tasks;
```

## Key Features of the Schema

### 1. Project-Centric Design
- All meetings and insights link to projects
- Automatic project assignment with confidence scoring
- Manual review flags for uncertain assignments

### 2. Comprehensive Tracking
- **Meetings**: Full transcript metadata and storage links
- **Chunks**: Vectorized content with speaker/timestamp info
- **Insights**: Categorized findings (general, positive, risks, actions)
- **Tasks**: Extracted action items with assignees and due dates
- **Sentiment**: Meeting and project-level sentiment analysis

### 3. Performance Optimizations
- Vector similarity search using ivfflat
- Trigram indexes for text search
- Strategic indexes on foreign keys and common queries
- Automatic timestamp updates via triggers

### 4. Security & Scalability
- Row Level Security (RLS) enabled
- Service role access for workers
- Authenticated user read access
- UUID primary keys for distributed systems

### 5. Feedback & Improvement
- User feedback tracking
- Chat session history
- Confidence scoring throughout

## Next Steps

1. **Ingest Worker**: Use the `sync_status` table to track progress
2. **Vectorize Worker**: Leverage the `search_chunks` function for similarity search
3. **Chat Worker**: Store sessions in `chat_sessions` and `chat_messages`
4. **Insights Worker**: Populate `project_insights` and `project_tasks`

The schema is designed to support all the functionality described in your project overview while maintaining flexibility for future enhancements.