import { Hono } from 'hono';
import { cors } from 'hono/cors';

// Define the worker environment interface
interface Env {
  DB: D1Database;
  AI: any; // Cloudflare AI binding
}

const app = new Hono<{ Bindings: Env }>();

// CORS middleware
app.use('*', cors({
  origin: ['http://localhost:3000', 'https://alleato.com'],
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization'],
}));

// Health check endpoint
app.get('/health', (c) => {
  return c.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    worker: 'insights-worker'
  });
});

// Main insights generation endpoint
app.post('/api/v1/insights/generate', async (c) => {
  try {
    const { meeting_id, type } = await c.req.json();
    
    if (!meeting_id) {
      return c.json({ error: 'meeting_id is required' }, 400);
    }

    // TODO: Implement insights generation logic
    // This is a placeholder implementation
    
    return c.json({
      meeting_id,
      type: type || 'summary',
      insights: {
        summary: 'Insights generation not yet implemented',
        key_points: [],
        action_items: [],
        sentiment: 'neutral',
        generated_at: new Date().toISOString()
      }
    });
    
  } catch (error) {
    console.error('Error generating insights:', error);
    return c.json({ error: 'Failed to generate insights' }, 500);
  }
});

// Batch insights generation
app.post('/api/v1/insights/batch', async (c) => {
  try {
    const { meeting_ids } = await c.req.json();
    
    if (!Array.isArray(meeting_ids) || meeting_ids.length === 0) {
      return c.json({ error: 'meeting_ids array is required' }, 400);
    }

    // TODO: Implement batch insights generation
    
    return c.json({
      status: 'queued',
      meeting_count: meeting_ids.length,
      estimated_completion: new Date(Date.now() + 5 * 60 * 1000).toISOString() // 5 minutes from now
    });
    
  } catch (error) {
    console.error('Error in batch insights generation:', error);
    return c.json({ error: 'Failed to queue batch insights generation' }, 500);
  }
});

// Get insights for a meeting
app.get('/api/v1/insights/:meeting_id', async (c) => {
  try {
    const meeting_id = c.req.param('meeting_id');
    
    // TODO: Fetch insights from database
    
    return c.json({
      meeting_id,
      insights: null,
      message: 'Insights retrieval not yet implemented'
    });
    
  } catch (error) {
    console.error('Error fetching insights:', error);
    return c.json({ error: 'Failed to fetch insights' }, 500);
  }
});

// 404 handler
app.notFound((c) => {
  return c.json({ error: 'Not found' }, 404);
});

// Error handler
app.onError((err, c) => {
  console.error('Unhandled error:', err);
  return c.json({ error: 'Internal server error' }, 500);
});

export default app;