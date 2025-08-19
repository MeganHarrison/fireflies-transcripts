import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { Ai } from '@cloudflare/ai';
import OpenAI from 'openai';
import { 
  Env, 
  ChatRequest, 
  ChatSession, 
  ChatMessage,
  RetrievedChunk 
} from './types';
import { RAGRetrieval } from './retrieval';
import { 
  buildSystemPrompt, 
  formatContext, 
  generateFollowUpQuestions,
  formatResponse 
} from './prompts';

const app = new Hono<{ Bindings: Env }>();

app.use('/*', cors());

// Main chat endpoint
app.post('/chat', async (c) => {
  const ai = new Ai(c.env.AI);
  const retrieval = new RAGRetrieval(c.env, ai);
  
  try {
    const request: ChatRequest = await c.req.json();
    const { query, projectId, chatHistory = [], mode = 'balanced' } = request;
    const sessionId = request.sessionId || crypto.randomUUID();

    // Track analytics
    c.env.ANALYTICS.writeDataPoint({
      blobs: [sessionId || 'anonymous', projectId || 'none', mode],
      doubles: [Date.now()],
      indexes: ['chat_request'],
    });

    // Check cache for similar queries
    const cacheKey = `${projectId || 'all'}:${query.toLowerCase().slice(0, 50)}`;
    const cached = await c.env.RESPONSE_CACHE.get(cacheKey);
    if (cached && mode === 'recall') {
      return c.json(JSON.parse(cached));
    }

    // LOG: Query details
    console.log('[AI Agent] Processing query:', {
      query,
      projectId,
      sessionId,
      mode,
      cacheKey
    });

    // Retrieve relevant chunks
    const chunks = await retrieval.retrieveRelevantChunks(query, projectId);
    
    // LOG: Retrieved chunks
    console.log('[AI Agent] Retrieved chunks:', {
      count: chunks.length,
      chunks: chunks.map(c => ({
        id: c.id,
        score: c.score,
        text: c.text.substring(0, 100) + '...',
        meetingId: c.meetingId,
        projectId: c.projectId
      }))
    });
    
    // Get project context if projectId provided
    const projectContext = projectId ? 
      await retrieval.getProjectContext(projectId) : 
      undefined;

    // LOG: Project context
    console.log('[AI Agent] Project context:', projectContext ? {
      projectId: projectContext.project?.id,
      title: projectContext.project?.title,
      activeTasks: projectContext.activeTasks?.length,
      recentInsights: projectContext.recentInsights?.length
    } : 'No project context');

    // Check for cross-project patterns if in strategy mode
    let crossProjectInsights = null;
    if (mode === 'strategy' && !projectId) {
      crossProjectInsights = await retrieval.findCrossProjectPatterns(query);
    }

    // Build context and system prompt
    const systemPrompt = buildSystemPrompt(mode);
    const context = formatContext(chunks, projectContext);
    
    // LOG: Context being sent to AI
    console.log('[AI Agent] Context for AI:', {
      systemPromptLength: systemPrompt.length,
      contextLength: context.length,
      contextPreview: context.substring(0, 200) + '...',
      hasChunks: chunks.length > 0,
      hasProjectContext: !!projectContext
    });
    
    // Prepare messages
    const messages: ChatMessage[] = [
      {
        role: 'system',
        content: `${systemPrompt}\n\nCONTEXT:\n${context}`,
      },
      ...chatHistory.slice(-5), // Keep last 5 messages for context
      {
        role: 'user',
        content: query,
      },
    ];

    // Generate response with OpenAI if API key available, otherwise use Cloudflare AI
    if (c.env.OPENAI_API_KEY && c.env.OPENAI_API_KEY.length > 0) {
      const openai = new OpenAI({
        apiKey: c.env.OPENAI_API_KEY,
      });

      const stream = await openai.chat.completions.create({
        model: 'gpt-4-turbo',
        messages: messages as any,
        stream: true,
        temperature: mode === 'recall' ? 0.3 : 0.7,
        max_tokens: 1000,
      });

      // Update session
      if (sessionId) {
        await updateChatSession(c.env, sessionId, projectId, messages, chunks);
      }

      // Convert OpenAI stream to SSE format and capture response
      const encoder = new TextEncoder();
      let fullResponse = '';
      const readable = new ReadableStream({
        async start(controller) {
          for await (const chunk of stream) {
            const text = chunk.choices[0]?.delta?.content || '';
            if (text) {
              fullResponse += text;
              const data = `data: ${JSON.stringify({ response: text })}\n\n`;
              controller.enqueue(encoder.encode(data));
            }
          }
          controller.enqueue(encoder.encode('data: [DONE]\n\n'));
          controller.close();
          
          // Save assistant message after streaming is complete
          if (sessionId) {
            await saveAssistantMessage(c.env, sessionId, fullResponse, 'gpt-4-turbo');
          }
        },
      });

      return new Response(readable, {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    } else {
      // Fallback to Cloudflare AI
      const response = await ai.run('@cf/meta/llama-3.1-8b-instruct', {
        messages: messages as any,
        stream: true,
        temperature: mode === 'recall' ? 0.3 : 0.7,
        max_tokens: 1000,
      });

      // Update session
      if (sessionId) {
        await updateChatSession(c.env, sessionId, projectId, messages, chunks);
      }

      // Capture response for saving
      let fullResponse = '';
      const encoder = new TextEncoder();
      const decoder = new TextDecoder();
      
      const transformStream = new TransformStream({
        async transform(chunk, controller) {
          controller.enqueue(chunk);
          
          // Capture the response text
          const text = decoder.decode(chunk, { stream: true });
          const lines = text.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ') && !line.includes('[DONE]')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.response) {
                  fullResponse += data.response;
                }
              } catch (e) {
                // Ignore parse errors
              }
            }
          }
        },
        async flush() {
          // Save assistant message after streaming is complete
          if (sessionId && fullResponse) {
            await saveAssistantMessage(c.env, sessionId, fullResponse, 'llama-3.1-8b');
          }
        }
      });

      // Return streaming response
      return new Response((response as ReadableStream).pipeThrough(transformStream), {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    }
  } catch (error) {
    console.error('Chat error:', error);
    return c.json({ 
      error: 'Failed to process chat request',
      details: error.message 
    }, 500);
  }
});

// Get chat session
app.get('/session/:sessionId', async (c) => {
  const sessionId = c.req.param('sessionId');
  
  try {
    const session = await c.env.CHAT_SESSIONS.get(sessionId);
    if (!session) {
      return c.json({ error: 'Session not found' }, 404);
    }
    
    return c.json(JSON.parse(session));
  } catch (error) {
    return c.json({ error: 'Failed to retrieve session' }, 500);
  }
});

// Provide feedback on response
app.post('/feedback', async (c) => {
  const { queryId, rating, feedback } = await c.req.json();
  
  try {
    await c.env.DB.prepare(`
      UPDATE rag_queries 
      SET feedback_rating = ?, feedback_text = ?
      WHERE id = ?
    `).bind(rating, feedback, queryId).run();
    
    // Track in analytics
    c.env.ANALYTICS.writeDataPoint({
      blobs: [queryId, feedback || ''],
      doubles: [rating, Date.now()],
      indexes: ['feedback'],
    });
    
    return c.json({ success: true });
  } catch (error) {
    return c.json({ error: 'Failed to save feedback' }, 500);
  }
});

// Get project summary
app.get('/project/:projectId/summary', async (c) => {
  const projectId = c.req.param('projectId');
  const ai = new Ai(c.env.AI);
  const retrieval = new RAGRetrieval(c.env, ai);
  
  try {
    const context = await retrieval.getProjectContext(projectId);
    
    // Get recent meeting summaries
    const summaries = await c.env.DB.prepare(`
      SELECT ms.*, m.title, m.date
      FROM meeting_summaries ms
      JOIN meetings m ON ms.meeting_id = m.id
      WHERE m.project = ?
      ORDER BY m.date DESC
      LIMIT 5
    `).bind(projectId).all();
    
    return c.json({
      project: context.project,
      sentiment: context.sentiment,
      activeTasks: context.activeTasks,
      recentInsights: context.recentInsights,
      recentMeetings: summaries.results.map((s: any) => ({
        title: s.title,
        date: s.date,
        summary: s.summary_short,
        keyPoints: JSON.parse(s.key_points || '[]'),
      })),
    });
  } catch (error) {
    return c.json({ error: 'Failed to get project summary' }, 500);
  }
});

// Helper functions
async function updateChatSession(
  env: Env,
  sessionId: string,
  projectId: string | undefined,
  messages: ChatMessage[],
  chunks: RetrievedChunk[],
  userId?: string
): Promise<void> {
  const now = new Date().toISOString();
  
  // Save to KV for quick access (2 hour cache)
  const session: ChatSession = {
    id: sessionId,
    projectId,
    messages: messages.slice(-10), // Keep last 10 messages
    context: {
      recentInsights: [],
      activeTasks: [],
      sentiment: { current: 0, trend: 'stable' },
    },
    createdAt: now,
    updatedAt: now,
  };
  
  await env.CHAT_SESSIONS.put(
    sessionId,
    JSON.stringify(session),
    { expirationTtl: 7200 } // 2 hour expiration
  );
  
  // Save to database for permanent storage
  try {
    // Check if session exists
    const existingSession = await env.DB.prepare(
      'SELECT id FROM ai_chat_sessions WHERE id = ?'
    ).bind(sessionId).first();
    
    if (!existingSession) {
      // Create new session
      const sessionTitle = messages.find(m => m.role === 'user')?.content.slice(0, 100) || 'New Chat';
      
      await env.DB.prepare(`
        INSERT INTO ai_chat_sessions (
          id, user_id, session_title, context_type, context_id,
          message_count, total_tokens_used, started_at, last_activity, session_context
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(
        sessionId,
        userId || null,
        sessionTitle,
        'project',
        projectId || null,
        messages.length,
        0, // TODO: Calculate actual tokens
        now,
        now,
        JSON.stringify({ chunks: chunks.length })
      ).run();
    } else {
      // Update existing session
      await env.DB.prepare(`
        UPDATE ai_chat_sessions 
        SET message_count = ?,
            last_activity = ?,
            session_context = ?
        WHERE id = ?
      `).bind(
        messages.length,
        now,
        JSON.stringify({ chunks: chunks.length }),
        sessionId
      ).run();
    }
    
    // Save the latest messages to ai_chat_messages
    const lastUserMessage = messages[messages.length - 2]; // Second to last is user
    const lastAssistantMessage = messages[messages.length - 1]; // Last is assistant
    
    if (lastUserMessage && lastUserMessage.role === 'user') {
      await env.DB.prepare(`
        INSERT INTO ai_chat_messages (
          id, session_id, role, content, model_used, confidence_score, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
      `).bind(
        crypto.randomUUID(),
        sessionId,
        'user',
        lastUserMessage.content,
        null,
        null,
        now
      ).run();
    }
    
    // Note: Assistant message will be saved after response is generated
  } catch (error) {
    console.error('Failed to save chat session to database:', error);
  }
}

async function logQuery(
  env: Env,
  query: string,
  chunks: RetrievedChunk[],
  response: string,
  sessionId?: string
): Promise<void> {
  const queryId = crypto.randomUUID();
  
  await env.DB.prepare(`
    INSERT INTO rag_queries (
      id, query_text, retrieved_chunks, response,
      relevance_scores, session_id, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
  `).bind(
    queryId,
    query,
    JSON.stringify(chunks.map(c => c.id)),
    response.substring(0, 1000), // Truncate for storage
    JSON.stringify(chunks.map(c => c.score)),
    sessionId,
    new Date().toISOString()
  ).run();
}

// Save assistant message to database
async function saveAssistantMessage(
  env: Env,
  sessionId: string,
  content: string,
  modelUsed: string,
  tokensUsed?: number
): Promise<void> {
  try {
    await env.DB.prepare(`
      INSERT INTO ai_chat_messages (
        id, session_id, role, content, model_used, tokens_used, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
    `).bind(
      crypto.randomUUID(),
      sessionId,
      'assistant',
      content,
      modelUsed,
      tokensUsed || 0,
      new Date().toISOString()
    ).run();
    
    // Update session token count
    if (tokensUsed) {
      await env.DB.prepare(`
        UPDATE ai_chat_sessions 
        SET total_tokens_used = total_tokens_used + ?
        WHERE id = ?
      `).bind(tokensUsed, sessionId).run();
    }
  } catch (error) {
    console.error('Failed to save assistant message:', error);
  }
}

// Get user's chat sessions
app.get('/sessions', async (c) => {
  const userId = c.req.query('userId');
  const limit = parseInt(c.req.query('limit') || '20');
  const offset = parseInt(c.req.query('offset') || '0');
  
  try {
    const sessions = await c.env.DB.prepare(`
      SELECT 
        id, 
        session_title, 
        context_type, 
        context_id,
        message_count,
        started_at,
        last_activity
      FROM ai_chat_sessions
      WHERE user_id = ? OR user_id IS NULL
      ORDER BY last_activity DESC
      LIMIT ? OFFSET ?
    `).bind(userId || null, limit, offset).all();
    
    return c.json({
      sessions: sessions.results,
      total: sessions.results.length,
      limit,
      offset
    });
  } catch (error) {
    console.error('Failed to get sessions:', error);
    return c.json({ error: 'Failed to retrieve sessions' }, 500);
  }
});

// Get messages for a specific session
app.get('/sessions/:sessionId/messages', async (c) => {
  const sessionId = c.req.param('sessionId');
  
  try {
    const messages = await c.env.DB.prepare(`
      SELECT 
        role,
        content,
        model_used,
        created_at
      FROM ai_chat_messages
      WHERE session_id = ?
      ORDER BY created_at ASC
    `).bind(sessionId).all();
    
    return c.json({
      sessionId,
      messages: messages.results
    });
  } catch (error) {
    console.error('Failed to get messages:', error);
    return c.json({ error: 'Failed to retrieve messages' }, 500);
  }
});

export default app;