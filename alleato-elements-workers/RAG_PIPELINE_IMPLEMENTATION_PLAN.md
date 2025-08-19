# RAG Pipeline Implementation Plan

## Overview
This document outlines the complete implementation plan for the Fireflies RAG pipeline using Cloudflare Workers. The pipeline consists of three core workers plus an insights generation component, with emphasis on project linking.

## Current State
- ✅ **Ingest Worker**: Currently working, syncing transcripts to D1 `meetings` table
- ⚠️ **Vectorize Worker**: Partial implementation exists, needs enhancement
- ✅ **AI Agent Chat Worker**: Functional with basic chat capabilities
- ❌ **Insights Worker**: Only skeleton exists
- ❌ **Project Linking**: Not implemented

## Database Schema
The complete schema is in `shared/complete-database-schema.sql`. Key additions:
- `projects` table for project management
- Project linking fields in `meetings` and `document_chunks`
- New tables: `project_insights`, `meeting_summaries`, `project_tasks`, `project_sentiment`
- Enhanced `ai_chat_messages` with feedback tracking

## Implementation Phases

### Phase 1: Database Migration (Do First)
1. Apply new schema to D1 database
2. Migrate existing data (add null project_id to existing records)
3. Create initial projects table entries

### Phase 2: Enhanced Vectorize Worker

#### Location: `/vectorize-worker/`
#### Key Enhancements:

**1. Intelligent Chunking Strategy**
```typescript
interface ChunkingStrategy {
  method: 'sentence' | 'semantic' | 'sliding_window';
  chunkSize: number; // tokens
  overlap: number; // tokens
  preserveBoundaries: boolean; // respect speaker changes
}
```

**2. Project Linking Logic**
```typescript
interface ProjectMatcher {
  // Matching heuristics (in priority order):
  titleKeywords: string[];      // Check meeting title
  participantEmails: string[];  // Check attendees
  contentKeywords: string[];    // Scan transcript content
  confidenceThreshold: number;  // Min score to auto-assign (0.7)
}
```

**3. Enhanced Processing Pipeline**
- Retrieve transcript from R2 storage
- Apply intelligent chunking with speaker preservation
- Generate embeddings using Cloudflare AI
- Determine project assignment using heuristics
- Store chunks with project context
- Queue insights generation task

**Implementation File Structure:**
```
/vectorize-worker/
  src/
    index.ts          # Main worker entry
    chunking.ts       # Chunking strategies
    project-matcher.ts # Project assignment logic
    embeddings.ts     # Vectorize integration
    types.ts          # TypeScript interfaces
```

### Phase 3: Insights Generation Component

#### Location: `/insights-worker/`
#### Core Functionality:

**1. Insight Categories**
```typescript
enum InsightCategory {
  GENERAL_INFO = 'general_info',      // Updates, decisions, facts
  POSITIVE_FEEDBACK = 'positive_feedback', // Wins, praise, progress
  RISKS = 'risks',                    // Blockers, concerns, issues
  ACTION_ITEMS = 'action_items'       // Tasks, deadlines, commitments
}
```

**2. Processing Pipeline**
```typescript
interface InsightsProcessor {
  analyzeMeeting(meetingId: string): Promise<void>;
  categorizeInsights(text: string): InsightCategory;
  extractEntities(text: string): Entity[];
  generateSummaries(chunks: Chunk[]): Summaries;
  extractTasks(insights: Insight[]): Task[];
  analyzeSentiment(chunks: Chunk[]): SentimentScore;
}
```

**3. AI Prompt Templates**
- Insight extraction prompt
- Summary generation (short/medium/long)
- Task extraction with assignee detection
- Sentiment analysis prompt

**Implementation Files:**
```
/insights-worker/
  src/
    index.ts           # Worker entry point
    analyzer.ts        # Main analysis logic
    prompts.ts         # AI prompt templates
    extractors/
      insights.ts      # Insight extraction
      tasks.ts         # Task extraction
      sentiment.ts     # Sentiment analysis
      summaries.ts     # Summary generation
```

### Phase 4: Enhanced AI Agent Chat Worker

#### Location: `/ai-agent-worker/`
#### Enhancements:

**1. Project-Aware Context**
```typescript
interface ChatContext {
  sessionId: string;
  projectId?: string;
  relevantInsights: ProjectInsight[];
  projectSentimentTrend: SentimentData[];
}
```

**2. Dual Expertise Implementation**
- **Project Recall Mode**: Retrieve and synthesize meeting details
- **Strategic Analysis Mode**: Cross-project pattern recognition

**3. Enhanced Retrieval**
```typescript
interface EnhancedRetrieval {
  // Multi-stage retrieval:
  vectorSearch(query: string, projectId?: string): Chunk[];
  insightSearch(query: string, category?: InsightCategory): Insight[];
  crossProjectAnalysis(pattern: string): CrossProjectInsight[];
}
```

**4. Feedback Integration**
- Track thumbs up/down per response
- Store categorized feedback
- Use feedback to improve retrieval ranking

### Phase 5: Cross-Worker Integration

#### Message Queue Flow:
```
Ingest Worker → Queue → Vectorize Worker
                  ↓
            Insights Worker
                  ↓
            AI Agent (reads all data)
```

#### Shared Libraries:
Create `/shared/` directory with:
- `database.ts` - D1 database utilities
- `types.ts` - Shared TypeScript interfaces
- `project-utils.ts` - Project matching utilities
- `ai-prompts.ts` - Reusable prompt templates

## Implementation Timeline

### Week 1: Foundation
- [ ] Apply database schema migration
- [ ] Create project management endpoints
- [ ] Set up shared libraries

### Week 2: Vectorize Worker
- [ ] Implement intelligent chunking
- [ ] Add project matching logic
- [ ] Update queue processing

### Week 3: Insights Worker
- [ ] Implement insight extraction
- [ ] Add summary generation
- [ ] Create task extraction

### Week 4: AI Agent Enhancement
- [ ] Add project-aware context
- [ ] Implement dual expertise modes
- [ ] Add feedback tracking

### Week 5: Testing & Optimization
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Documentation

## Key Technical Decisions

### 1. Embedding Strategy
- Use Cloudflare AI `@cf/baai/bge-base-en-v1.5` (768 dimensions)
- Chunk size: 800 tokens with 200 token overlap
- Preserve speaker boundaries in chunks

### 2. Project Assignment
- Automatic assignment when confidence > 0.7
- Flag for manual review when confidence 0.4-0.7
- Unassigned when confidence < 0.4

### 3. Queue Processing
- Priority levels: 1 (vectorize) → 2 (summarize) → 3 (insights) → 4 (tasks)
- Retry failed operations up to 3 times
- Dead letter queue for persistent failures

### 4. AI Models
- Embeddings: Cloudflare AI (free, fast)
- Chat: GPT-4 for complex queries, Llama 3 for simple ones
- Insights: GPT-3.5-turbo (balance of cost/quality)

## Monitoring & Metrics

### Key Metrics to Track:
- Transcripts processed per hour
- Average processing time per transcript
- Project assignment accuracy
- Insight extraction precision
- Chat response satisfaction
- Vector search latency

### Error Handling:
- Comprehensive logging to console
- Error tracking in processing_queue table
- Alerting on repeated failures
- Graceful degradation (e.g., proceed without project if matching fails)

## Security Considerations

1. **API Keys**: Store in Worker secrets, never in code
2. **Data Access**: Use service role keys with minimal permissions
3. **User Context**: Validate user access to projects
4. **PII Handling**: Be mindful of personal information in transcripts

## Next Steps

1. Review and approve this plan
2. Set up development environment
3. Create feature branches for each worker
4. Begin implementation with Phase 1 (Database Migration)

## Success Criteria

- [ ] All transcripts automatically linked to projects (or flagged for review)
- [ ] Insights generated within 5 minutes of transcript ingestion
- [ ] AI agent can answer project-specific questions with context
- [ ] Dashboard shows categorized insights per project
- [ ] User feedback improves system accuracy over time