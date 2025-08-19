# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
## Project Overview

We need to finalize the RAG (Retrieval-Augmented Generation) pipeline using Supabase, Cloudflare Workers, and Fireflies meeting transcripts. The pipeline will consist of three core workers, plus an insights-generation component, with a strong emphasis on linking every transcript and its insights to a specific project.

### Ingest Worker

- Purpose: Sync transcripts from Fireflies into Supabase storage bucket.
- Deliverable: A worker that reliably keeps meetings up-to-date with Fireflies.
- Functionality
    - Run on a schedule (e.g., cron trigger).
    - Query Fireflies API for any new transcripts since the last sync.
    - Insert new transcripts into the Supabase storage bucket and adds to the meetings table with a link to the file in the storage bucket.
    - Ensure no duplicate records are inserted (use transcript id as a unique key).
    - Store raw metadata such as: title, participants, timestamps, and meeting duration.

### Vectorize Worker

- Purpose: Convert transcripts into high-quality embeddings and link them to projects.
- Deliverable: A worker that vectorizes transcripts into embeddings, intelligently assigns them to projects, and ensures all data is queryable for retrieval.
- Functionality:
    - Trigger when a new record is added to meetings.
    - Use intelligent chunking (sentence or semantic overlap) to optimize retrieval quality.
    - Generate embeddings for each chunk and insert them into the chunks table.
    - Metadata stored per chunk: transcript ID, project ID, speaker info, timestamps.
    - Project Linking:
        - Scan transcript metadata and text to infer the correct project_id.
        - Heuristics may include: Title matching (project name keywords), Participant matching (team members assigned to projects), Keyword/topic matching (common terminology per project).
            - If confidence is low, flag transcript for human review but still store with a placeholder project link.

### AI Agent Chat Worker

- Purpose: Act as the user-facing Project Manager + Business Strategist AI agent.
- Deliverable: A chat worker that transforms transcript knowledge into strategic, actionable conversations.
- Functionality:
•	Provide a chat API endpoint for the front-end.
•	Retrieve relevant chunks from the chunks table via semantic search.
•	Maintain dual expertise:
•	Project Recall → Summarize, explain, and answer details from transcripts.
•	Business Strategy → Recognize cross-project patterns and provide higher-level recommendations.
•	Generate contextual answers, insights, and action-oriented recommendations.
•	Include mechanisms for user feedback (thumbs up/down, categorization) to improve retrieval quality.

### Insights Generation Component

(This may be part of the Vectorize Worker or a separate Insights Worker.)

- Purpose: Automatically generate structured insights and attach them to projects.
- Deliverable: Structured, project-linked insights available for dashboards and summaries.
- Functionality:
•	After ingestion/vectorization, analyze each transcript for insights.
•	Categorize insights into types:
•	General Information → status updates, decisions, facts.
•	Positive Feedback → wins, praise, progress signals.
•	Risks / Negative Feedback → blockers, concerns, issues.
•	Action Items → follow-ups, deadlines, commitments.
•	Insert insights into a project_insights table with columns: insight_id, project_id, meeting_id, category, text, confidence_score.

### Extended Functionality (Deeper Enhancements)

- Summarization: Each transcript also generates a meeting summary (short, medium, long versions) stored in meeting_summaries.
- Sentiment Analysis: Perform sentiment scoring at both meeting and project levels to spot overall morale and tone.
- Action Item Extraction: Automatically identify tasks, deadlines, and owners, and store them in project_tasks.
- Feedback Loop:
- Allow users to confirm or reject project linking.
- Let users edit/categorize insights directly from the dashboard to refine accuracy.
- Cross-Project Analysis: Enable the agent to surface patterns across multiple projects (e.g., recurring risks, common blockers, successful strategies).

### Integration Notes

Front End:

- Project Details Page: Show categorized insights (project_insights) + summaries + sentiment trend.
- Chat Interface: Connect to the AI Agent Chat Worker API.
- Task View (Optional): Display extracted action items linked back to the source transcript.
- Scalability: Ensure workers can process large transcript volumes without timeouts (consider batching).
- Design chunking/vectorization as modular so we can experiment with strategies (e.g., dynamic chunk size, semantic overlap).

### Expected Output:

A fully functional, intelligent pipeline where:
1.	Transcripts are synced from Fireflies (Ingest Worker).
2.	Transcripts are vectorized, chunked, and linked to projects (Vectorize Worker).
3.	An AI chat agent retrieves knowledge and advises strategically (AI Chat Worker).
4.	Insights, summaries, tasks, and sentiment analysis are generated and stored for project dashboards (Insights Component).
5.	Users can interact with and refine insights, ensuring continuous improvement of the system.

👉 This way, the AI agent isn’t just a knowledge base — it evolves into a strategic project partner that manages details, surfaces risks, and amplifies wins.


This is a Python-based data pipeline for processing Fireflies.ai meeting transcripts. The system downloads transcripts via GraphQL API, converts them to Markdown, generates embeddings using OpenAI, and stores them in Supabase for vector search.

## Key Commands

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the webhook server (default port 8000)
uvicorn fireflies_webhook_pipeline:app --reload

# For production deployment
uvicorn fireflies_webhook_pipeline:app --host 0.0.0.0 --port 8000
```

### Manual Script Execution

```bash
# Download and convert specific transcript
python fireflies_client.py  # Modify main() function for specific transcript IDs

# Convert JSON transcript to Markdown
python markdown_converter.py  # Requires JSON input file
```

## Architecture

### Core Components

1. **fireflies_client.py**: GraphQL client for Fireflies.ai API
   - `FirefliesClient` class handles authentication and API requests
   - Methods: `get_transcript_list()`, `get_transcript_by_id()`
   - Uses Fireflies API key from environment

2. **markdown_converter.py**: JSON to Markdown conversion
   - `convert_transcript_to_markdown()` processes transcript structure
   - `save_markdown_file()` handles file sanitization and storage
   - Maps speaker IDs to human-readable names

3. **fireflies_webhook_pipeline.py**: FastAPI webhook server
   - Endpoint: `POST /webhook/transcript` - processes new transcripts
   - Pipeline: Download � Convert � Chunk � Embed � Store
   - Uses tiktoken for intelligent text chunking (800 tokens with 200 overlap)
   - Generates ada-002 embeddings via OpenAI
   - Stores in Supabase table `meeting_chunks` with vector search

### Data Flow

1. Fireflies.ai webhook triggers on new transcript
2. FastAPI endpoint receives transcript ID
3. GraphQL API fetches full transcript data
4. Converter creates Markdown file in `transcripts/` directory
5. Text chunker splits content preserving context
6. OpenAI generates embeddings for each chunk
7. Supabase stores chunks with metadata and vectors

## Environment Configuration

Required `.env` variables:
```
FIREFLIES_API_KEY=your_fireflies_api_key
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key
```

## Database Schema

Supabase table `meeting_chunks`:
- `id`: Primary key
- `meeting_title`: String
- `meeting_date`: Date
- `chunk_index`: Integer
- `content`: Text
- `embedding`: Vector(1536)
- `metadata`: JSONB (speakers, duration, etc.)

## Development Notes

- No test suite exists - consider adding pytest when implementing new features
- No linting configuration - consider adding black/flake8 for consistency
- Webhook endpoint lacks input validation - add Pydantic models for safety
- No rate limiting - consider adding for production deployment
- Logs print to stdout - consider structured logging for production