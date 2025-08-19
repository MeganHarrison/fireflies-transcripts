import { Ai } from '@cloudflare/ai';
import { Env, RetrievedChunk, ProjectContext } from './types';

export class RAGRetrieval {
  constructor(
    private env: Env,
    private ai: Ai
  ) {}

  async retrieveRelevantChunks(
    query: string,
    projectId?: string,
    topK: number = 5
  ): Promise<RetrievedChunk[]> {
    console.log('[RAG Retrieval] Starting chunk retrieval:', {
      query,
      projectId,
      topK
    });

    try {
      // Generate query embedding
      const embeddingResponse = await this.ai.run('@cf/baai/bge-base-en-v1.5', {
        text: query,
      });
      
      const queryEmbedding = embeddingResponse.data[0];
      console.log('[RAG Retrieval] Generated embedding:', {
        embeddingLength: queryEmbedding?.length,
        firstValues: queryEmbedding?.slice(0, 5)
      });

      // Search with optional project filter
      const searchOptions: any = {
        topK: topK * 2, // Get more results for reranking
        returnMetadata: true,
      };

      if (projectId) {
        searchOptions.filter = { projectId };
      }

      console.log('[RAG Retrieval] Searching vector index with options:', searchOptions);
      const searchResults = await this.env.VECTOR_INDEX.query(
        queryEmbedding,
        searchOptions
      );
      
      console.log('[RAG Retrieval] Vector search results:', {
        matchCount: searchResults.matches?.length || 0,
        matches: searchResults.matches?.slice(0, 3).map(m => ({
          id: m.id,
          score: m.score,
          metadata: m.metadata
        }))
      });

      // Fetch chunk details from database
      const chunkIds = searchResults.matches.map(m => m.id);
      if (chunkIds.length === 0) {
        console.log('[RAG Retrieval] No matches found in vector index');
        return [];
      }

    const placeholders = chunkIds.map(() => '?').join(',');
    console.log('[RAG Retrieval] Fetching chunk details for IDs:', chunkIds.slice(0, 5));
    
    const chunks = await this.env.DB.prepare(`
      SELECT dc.*, m.title as meeting_title, m.date as meeting_date,
             p.title as project_title
      FROM document_chunks dc
      JOIN meetings m ON dc.meeting_id = m.id
      LEFT JOIN projects p ON dc.project_id = p.id
      WHERE dc.id IN (${placeholders})
    `).bind(...chunkIds).all();
    
    console.log('[RAG Retrieval] Database results:', {
      rowCount: chunks.results?.length || 0,
      sampleRow: chunks.results?.[0]
    });

    // Map and rerank results
    const retrievedChunks: RetrievedChunk[] = [];
    
    for (const match of searchResults.matches) {
      const chunk = chunks.results.find((c: any) => c.id === match.id);
      if (chunk) {
        retrievedChunks.push({
          id: chunk.id as string,
          text: chunk.chunk_text as string,
          score: match.score,
          meetingId: chunk.meeting_id as string,
          projectId: chunk.project_id as string,
          metadata: {
            meetingTitle: chunk.meeting_title,
            meetingDate: chunk.meeting_date,
            projectTitle: chunk.project_title,
            speakers: JSON.parse(chunk.speaker_info as string || '[]'),
            startTime: chunk.chunk_start_time,
            endTime: chunk.chunk_end_time,
          },
        });
      }
    }
    
    console.log('[RAG Retrieval] Retrieved chunks before reranking:', {
      count: retrievedChunks.length,
      chunks: retrievedChunks.slice(0, 2).map(c => ({
        id: c.id,
        score: c.score,
        meetingTitle: c.metadata?.meetingTitle,
        textPreview: c.text.substring(0, 50) + '...'
      }))
    });

    // Rerank by relevance and recency
    const reranked = await this.rerankChunks(retrievedChunks, query, topK);
    console.log('[RAG Retrieval] Final reranked chunks:', {
      count: reranked.length,
      topChunk: reranked[0] ? {
        id: reranked[0].id,
        score: reranked[0].score,
        meetingTitle: reranked[0].metadata?.meetingTitle
      } : null
    });
    
    return reranked;
    } catch (error) {
      console.error('[RAG Retrieval] Error retrieving chunks:', error);
      return [];
    }
  }

  private async rerankChunks(
    chunks: RetrievedChunk[],
    query: string,
    topK: number
  ): Promise<RetrievedChunk[]> {
    // Simple reranking based on score and recency
    const now = new Date();
    
    const reranked = chunks.map(chunk => {
      let adjustedScore = chunk.score;
      
      // Boost recent meetings
      if (chunk.metadata?.meetingDate) {
        const meetingDate = new Date(chunk.metadata.meetingDate);
        const daysSince = (now.getTime() - meetingDate.getTime()) / (1000 * 60 * 60 * 24);
        
        if (daysSince < 7) {
          adjustedScore *= 1.2; // 20% boost for meetings within last week
        } else if (daysSince < 30) {
          adjustedScore *= 1.1; // 10% boost for meetings within last month
        }
      }
      
      // Boost if query terms appear in chunk
      const queryTerms = query.toLowerCase().split(/\s+/);
      const chunkLower = chunk.text.toLowerCase();
      const termMatches = queryTerms.filter(term => chunkLower.includes(term)).length;
      adjustedScore *= (1 + termMatches * 0.1);
      
      return { ...chunk, score: adjustedScore };
    });
    
    // Sort by adjusted score and return top K
    reranked.sort((a, b) => b.score - a.score);
    return reranked.slice(0, topK);
  }

  async getProjectContext(projectId: string): Promise<ProjectContext> {
    // Fetch project details
    const project = await this.env.DB.prepare(
      'SELECT * FROM projects WHERE id = ?'
    ).bind(projectId).first();

    // Fetch recent insights
    const insights = await this.env.DB.prepare(`
      SELECT pi.category, pi.text, m.date as meeting_date
      FROM project_insights pi
      JOIN meetings m ON pi.meeting_id = m.id
      WHERE pi.project_id = ?
      ORDER BY pi.created_at DESC
      LIMIT 10
    `).bind(projectId).all();

    // Fetch active tasks
    const tasks = await this.env.DB.prepare(`
      SELECT task_description as description, assigned_to, due_date, priority
      FROM project_tasks
      WHERE project_id = ? AND status IN ('pending', 'in_progress')
      ORDER BY 
        CASE priority 
          WHEN 'critical' THEN 1
          WHEN 'high' THEN 2
          WHEN 'medium' THEN 3
          WHEN 'low' THEN 4
        END,
        due_date ASC
      LIMIT 10
    `).bind(projectId).all();

    // Calculate sentiment trend
    const sentimentData = await this.env.DB.prepare(`
      SELECT ms.sentiment_score, m.date
      FROM meeting_summaries ms
      JOIN meetings m ON ms.meeting_id = m.id
      WHERE m.project = ?
      ORDER BY m.date DESC
      LIMIT 5
    `).bind(projectId).all();

    let currentSentiment = 0;
    let trend: 'improving' | 'stable' | 'declining' = 'stable';
    
    if (sentimentData.results.length > 0) {
      currentSentiment = sentimentData.results[0].sentiment_score as number;
      
      if (sentimentData.results.length > 2) {
        const recent = sentimentData.results.slice(0, 2).reduce((sum: number, r: any) => sum + r.sentiment_score, 0) / 2;
        const older = sentimentData.results.slice(2).reduce((sum: number, r: any) => sum + r.sentiment_score, 0) / (sentimentData.results.length - 2);
        
        if (recent > older + 0.1) trend = 'improving';
        else if (recent < older - 0.1) trend = 'declining';
      }
    }

    return {
      project: project ? {
        id: project.id as string,
        title: project.title as string,
        status: project.status_name as string,
        client: project.client_id as string,
      } : undefined,
      recentInsights: insights.results.map((i: any) => ({
        category: i.category,
        text: i.text,
        meetingDate: i.meeting_date,
      })),
      activeTasks: tasks.results.map((t: any) => ({
        description: t.description,
        assignedTo: t.assigned_to,
        dueDate: t.due_date,
        priority: t.priority,
      })),
      sentiment: {
        current: currentSentiment,
        trend,
      },
    };
  }

  async findCrossProjectPatterns(query: string): Promise<any> {
    // Search across all projects for patterns
    const chunks = await this.retrieveRelevantChunks(query, undefined, 10);
    
    // Group by project
    const projectGroups = new Map<string, RetrievedChunk[]>();
    for (const chunk of chunks) {
      if (chunk.projectId) {
        if (!projectGroups.has(chunk.projectId)) {
          projectGroups.set(chunk.projectId, []);
        }
        projectGroups.get(chunk.projectId)!.push(chunk);
      }
    }

    // Analyze patterns
    const patterns = {
      commonThemes: new Map<string, number>(),
      recurringIssues: [],
      successPatterns: [],
      projectCount: projectGroups.size,
    };

    // Extract themes using simple keyword analysis
    const allText = chunks.map(c => c.text).join(' ').toLowerCase();
    const words = allText.split(/\s+/);
    const wordFreq = new Map<string, number>();
    
    for (const word of words) {
      if (word.length > 4) { // Skip short words
        wordFreq.set(word, (wordFreq.get(word) || 0) + 1);
      }
    }

    // Get top themes
    const sortedWords = Array.from(wordFreq.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);
    
    for (const [word, count] of sortedWords) {
      patterns.commonThemes.set(word, count);
    }

    return patterns;
  }
}