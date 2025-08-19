import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { FirefliesAPI } from './fireflies-api';
import { Env, FirefliesTranscript, SyncState, ProcessingTask } from './types';

const app = new Hono<{ Bindings: Env }>();

app.use('/*', cors());

// Manual sync endpoint
app.post('/sync', async (c) => {
  try {
    const result = await syncTranscripts(c.env);
    return c.json({ success: true, result });
  } catch (error) {
    console.error('Sync error:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Get sync status
app.get('/status', async (c) => {
  try {
    const state = await getSyncState(c.env);
    return c.json({ success: true, state });
  } catch (error) {
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Scheduled handler for cron jobs
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    return app.fetch(request, env);
  },

  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    ctx.waitUntil(syncTranscripts(env));
  },
};

async function syncTranscripts(env: Env): Promise<{ synced: number; errors: number }> {
  const fireflies = new FirefliesAPI(env.FIREFLIES_API_KEY, env.FIREFLIES_API_URL);
  const state = await getSyncState(env);
  
  let synced = 0;
  let errors = 0;
  
  try {
    // Fetch transcripts since last successful sync
    const transcripts = await fireflies.getTranscripts(
      state.lastSuccessfulSync || undefined
    );
    
    console.log(`Found ${transcripts.length} transcripts to process`);
    
    for (const transcript of transcripts) {
      try {
        // Check if transcript already exists
        const existing = await env.DB.prepare(
          'SELECT id FROM meetings WHERE fireflies_id = ?'
        ).bind(transcript.id).first();
        
        if (!existing) {
          await insertTranscript(env, transcript);
          await queueProcessingTasks(env, transcript.id);
          synced++;
        } else {
          // Update existing transcript if needed
          await updateTranscript(env, transcript);
        }
      } catch (error) {
        console.error(`Error processing transcript ${transcript.id}:`, error);
        errors++;
      }
    }
    
    // Update sync state
    await updateSyncState(env, {
      lastSyncTimestamp: new Date().toISOString(),
      lastSuccessfulSync: new Date().toISOString(),
      totalSynced: state.totalSynced + synced,
      lastError: errors > 0 ? `Synced ${synced} with ${errors} errors` : null,
    });
    
  } catch (error) {
    console.error('Sync failed:', error);
    await updateSyncState(env, {
      lastSyncTimestamp: new Date().toISOString(),
      lastError: error.message,
    });
    throw error;
  }
  
  return { synced, errors };
}

async function insertTranscript(env: Env, transcript: FirefliesTranscript): Promise<void> {
  // Generate unique ID for the meeting
  const meetingId = crypto.randomUUID();
  
  // Store transcript content in R2 if available
  let r2Key: string | null = null;
  if (transcript.sentences && transcript.sentences.length > 0) {
    r2Key = `transcripts/${meetingId}.json`;
    await env.R2.put(r2Key, JSON.stringify(transcript.sentences));
  }
  
  // Prepare transcript preview (first 500 chars)
  const transcriptPreview = transcript.sentences
    ?.slice(0, 5)
    .map(s => `${s.speaker_name}: ${s.text}`)
    .join(' ')
    .substring(0, 500);
  
  // Insert into meetings table
  await env.DB.prepare(`
    INSERT INTO meetings (
      id, fireflies_id, title, date, duration, participants,
      summary, transcript_url, organizer_email, meeting_url,
      r2_key, transcript_preview, created_at, updated_at,
      vector_processed, insight_generated
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    meetingId,
    transcript.id,
    transcript.title,
    transcript.date,
    transcript.duration,
    JSON.stringify(transcript.participants),
    transcript.summary,
    transcript.transcript_url,
    transcript.organizer_email,
    transcript.meeting_url,
    r2Key,
    transcriptPreview,
    new Date().toISOString(),
    new Date().toISOString(),
    false,
    false
  ).run();
  
  console.log(`Inserted transcript ${transcript.id} as meeting ${meetingId}`);
}

async function updateTranscript(env: Env, transcript: FirefliesTranscript): Promise<void> {
  // Update existing transcript with new data
  await env.DB.prepare(`
    UPDATE meetings 
    SET title = ?, summary = ?, updated_at = ?
    WHERE fireflies_id = ?
  `).bind(
    transcript.title,
    transcript.summary,
    new Date().toISOString(),
    transcript.id
  ).run();
}

async function queueProcessingTasks(env: Env, meetingId: string): Promise<void> {
  // Queue processing tasks for the new transcript
  const tasks: ProcessingTask[] = [
    { meetingId, operation: 'vectorize', priority: 1 },
    { meetingId, operation: 'summarize', priority: 2 },
    { meetingId, operation: 'generate_insights', priority: 3 },
    { meetingId, operation: 'extract_tasks', priority: 4 },
  ];
  
  for (const task of tasks) {
    await env.PROCESSING_QUEUE.send(task);
    
    // Also insert into DB queue for tracking
    await env.DB.prepare(`
      INSERT INTO processing_queue (
        id, source_id, source_type, operation, status, priority, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
    `).bind(
      crypto.randomUUID(),
      meetingId,
      'meeting',
      task.operation,
      'pending',
      task.priority,
      new Date().toISOString()
    ).run();
  }
}

async function getSyncState(env: Env): Promise<SyncState> {
  const result = await env.DB.prepare(
    'SELECT * FROM fireflies_sync_state WHERE id = ?'
  ).bind('singleton').first();
  
  if (!result) {
    return {
      lastSyncTimestamp: null,
      lastSuccessfulSync: null,
      totalSynced: 0,
      lastError: null,
      syncCursor: null,
    };
  }
  
  return {
    lastSyncTimestamp: result.last_sync_timestamp as string,
    lastSuccessfulSync: result.last_successful_sync as string,
    totalSynced: result.total_synced as number,
    lastError: result.last_error as string,
    syncCursor: result.sync_cursor as string,
  };
}

async function updateSyncState(env: Env, updates: Partial<SyncState>): Promise<void> {
  const params = [];
  const sets = [];
  
  if (updates.lastSyncTimestamp !== undefined) {
    sets.push('last_sync_timestamp = ?');
    params.push(updates.lastSyncTimestamp);
  }
  if (updates.lastSuccessfulSync !== undefined) {
    sets.push('last_successful_sync = ?');
    params.push(updates.lastSuccessfulSync);
  }
  if (updates.totalSynced !== undefined) {
    sets.push('total_synced = ?');
    params.push(updates.totalSynced);
  }
  if (updates.lastError !== undefined) {
    sets.push('last_error = ?');
    params.push(updates.lastError);
  }
  if (updates.syncCursor !== undefined) {
    sets.push('sync_cursor = ?');
    params.push(updates.syncCursor);
  }
  
  params.push('singleton'); // WHERE id = ?
  
  await env.DB.prepare(`
    UPDATE fireflies_sync_state 
    SET ${sets.join(', ')}, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
  `).bind(...params).run();
}