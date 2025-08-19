import { Ai } from '@cloudflare/ai';
import { Env, ProcessingMessage, Meeting, TranscriptSentence } from './types';
import { TranscriptChunker } from './chunking';
import { ProjectMatcher } from './project-matcher';

export default {
  async queue(batch: MessageBatch<ProcessingMessage>, env: Env): Promise<void> {
    for (const message of batch.messages) {
      try {
        await processMessage(message.body, env);
        message.ack();
      } catch (error) {
        console.error(`Error processing message:`, error);
        message.retry();
      }
    }
  },
};

async function processMessage(message: ProcessingMessage, env: Env): Promise<void> {
  console.log(`Processing ${message.operation} for meeting ${message.meetingId}`);

  switch (message.operation) {
    case 'vectorize':
      await vectorizeMeeting(message.meetingId, env);
      break;
    case 'summarize':
      await summarizeMeeting(message.meetingId, env);
      break;
    case 'generate_insights':
      await generateInsights(message.meetingId, env);
      break;
    case 'extract_tasks':
      await extractTasks(message.meetingId, env);
      break;
    default:
      console.error(`Unknown operation: ${message.operation}`);
  }

  // Update processing queue status
  await env.DB.prepare(`
    UPDATE processing_queue 
    SET status = 'completed', completed_at = CURRENT_TIMESTAMP
    WHERE source_id = ? AND operation = ?
  `).bind(message.meetingId, message.operation).run();
}

async function vectorizeMeeting(meetingId: string, env: Env): Promise<void> {
  const ai = new Ai(env.AI);
  
  // Fetch meeting details
  const meeting = await env.DB.prepare(
    'SELECT * FROM meetings WHERE id = ?'
  ).bind(meetingId).first<Meeting>();

  if (!meeting) {
    throw new Error(`Meeting ${meetingId} not found`);
  }

  // Load transcript from R2
  let sentences: TranscriptSentence[] = [];
  if (meeting.r2_key) {
    const transcriptData = await env.R2.get(meeting.r2_key);
    if (transcriptData) {
      sentences = await transcriptData.json();
    }
  }

  if (sentences.length === 0) {
    console.log(`No transcript data for meeting ${meetingId}`);
    return;
  }

  // Match to project
  const projectMatcher = new ProjectMatcher(env.DB);
  await projectMatcher.loadProjects();
  
  const fullTranscript = sentences.map(s => s.text).join(' ');
  const projectMatch = await projectMatcher.matchMeetingToProject(meeting, fullTranscript);
  
  let projectId = meeting.project;
  if (projectMatch && projectMatch.confidence > 0.5) {
    projectId = projectMatch.projectId;
    
    // Update meeting with matched project
    await env.DB.prepare(
      'UPDATE meetings SET project = ? WHERE id = ?'
    ).bind(projectId, meetingId).run();
    
    console.log(`Matched meeting to project ${projectId} with confidence ${projectMatch.confidence}`);
  }

  // Create chunks
  const chunker = new TranscriptChunker();
  const chunks = chunker.createChunks(sentences);
  
  console.log(`Created ${chunks.length} chunks for meeting ${meetingId}`);

  // Generate embeddings and store chunks
  const vectors = [];
  
  for (let i = 0; i < chunks.length; i++) {
    const chunk = chunks[i];
    const chunkId = `${meetingId}_chunk_${i}`;
    
    // Generate embedding
    const embeddingResponse = await ai.run('@cf/baai/bge-base-en-v1.5', {
      text: chunk.text,
    });
    
    const embedding = embeddingResponse.data[0];
    
    // Prepare vector for Vectorize
    vectors.push({
      id: chunkId,
      values: embedding,
      metadata: {
        meetingId,
        projectId,
        chunkIndex: i,
        startTime: chunk.startTime,
        endTime: chunk.endTime,
        speakers: Array.from(chunk.speakers),
      },
    });
    
    // Store chunk in database
    await env.DB.prepare(`
      INSERT INTO document_chunks (
        id, meeting_id, project_id, chunk_index, chunk_text,
        chunk_start_time, chunk_end_time, speaker_info, embedding_id,
        metadata, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      chunkId,
      meetingId,
      projectId,
      i,
      chunk.text,
      chunk.startTime,
      chunk.endTime,
      JSON.stringify(Array.from(chunk.speakers)),
      chunkId, // embedding_id references Vectorize
      JSON.stringify({
        sentenceCount: chunk.sentenceCount,
        chunkSize: chunk.text.length,
      }),
      new Date().toISOString()
    ).run();
  }

  // Insert vectors into Vectorize index
  if (vectors.length > 0) {
    await env.VECTOR_INDEX.insert(vectors);
  }

  // Mark meeting as vectorized
  await env.DB.prepare(
    'UPDATE meetings SET vector_processed = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?'
  ).bind(meetingId).run();
  
  console.log(`Vectorization complete for meeting ${meetingId}`);
}

async function summarizeMeeting(meetingId: string, env: Env): Promise<void> {
  const ai = new Ai(env.AI);
  
  // Fetch meeting and chunks
  const meeting = await env.DB.prepare(
    'SELECT * FROM meetings WHERE id = ?'
  ).bind(meetingId).first<Meeting>();

  if (!meeting) {
    throw new Error(`Meeting ${meetingId} not found`);
  }

  const chunks = await env.DB.prepare(
    'SELECT chunk_text FROM document_chunks WHERE meeting_id = ? ORDER BY chunk_index'
  ).bind(meetingId).all();

  if (chunks.results.length === 0) {
    console.log(`No chunks found for meeting ${meetingId}`);
    return;
  }

  // Concatenate chunks (limit to first 10 for context window)
  const text = chunks.results
    .slice(0, 10)
    .map(c => c.chunk_text)
    .join('\n\n');

  // Generate summaries
  const summaryPrompts = {
    short: 'Summarize this meeting transcript in 1-2 sentences, focusing on the main outcome or decision:',
    medium: 'Provide a one paragraph summary of this meeting, including key topics discussed and decisions made:',
    long: 'Create a detailed summary of this meeting, organized by topics, including all important decisions, action items, and discussion points:',
  };

  const summaries: any = {};
  
  for (const [type, prompt] of Object.entries(summaryPrompts)) {
    const response = await ai.run('@cf/meta/llama-2-7b-chat-int8', {
      prompt: `${prompt}\n\n${text}`,
      max_tokens: type === 'long' ? 500 : type === 'medium' ? 150 : 50,
    });
    
    summaries[`summary_${type}`] = response.response;
  }

  // Extract key points
  const keyPointsResponse = await ai.run('@cf/meta/llama-2-7b-chat-int8', {
    prompt: `List the 3-5 most important points from this meeting transcript as a JSON array:\n\n${text}`,
    max_tokens: 200,
  });

  let keyPoints = [];
  try {
    keyPoints = JSON.parse(keyPointsResponse.response);
  } catch {
    keyPoints = keyPointsResponse.response.split('\n').filter((p: string) => p.trim());
  }

  // Simple sentiment analysis
  const sentimentResponse = await ai.run('@cf/huggingface/distilbert-sst-2-int8', {
    text: summaries.summary_medium,
  });
  
  const sentimentScore = sentimentResponse.label === 'POSITIVE' ? 
    sentimentResponse.score : -sentimentResponse.score;

  // Insert summary
  await env.DB.prepare(`
    INSERT OR REPLACE INTO meeting_summaries (
      id, meeting_id, summary_short, summary_medium, summary_long,
      key_points, sentiment_score, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    crypto.randomUUID(),
    meetingId,
    summaries.summary_short,
    summaries.summary_medium,
    summaries.summary_long,
    JSON.stringify(keyPoints),
    sentimentScore,
    new Date().toISOString()
  ).run();

  console.log(`Summary generation complete for meeting ${meetingId}`);
}

async function generateInsights(meetingId: string, env: Env): Promise<void> {
  const ai = new Ai(env.AI);
  
  // Fetch meeting details and summary
  const meeting = await env.DB.prepare(`
    SELECT m.*, ms.summary_long, ms.key_points, p.title as project_title
    FROM meetings m
    LEFT JOIN meeting_summaries ms ON m.id = ms.meeting_id
    LEFT JOIN projects p ON m.project = p.id
    WHERE m.id = ?
  `).bind(meetingId).first();

  if (!meeting) {
    throw new Error(`Meeting ${meetingId} not found`);
  }

  const projectId = meeting.project as string;
  if (!projectId) {
    console.log(`No project assigned to meeting ${meetingId}`);
    return;
  }

  // Fetch chunks for detailed analysis
  const chunks = await env.DB.prepare(
    'SELECT chunk_text FROM document_chunks WHERE meeting_id = ? ORDER BY chunk_index LIMIT 20'
  ).bind(meetingId).all();

  const fullText = chunks.results.map(c => c.chunk_text).join('\n\n');

  // Generate categorized insights
  const insightPrompts = {
    general_info: 'Extract general information, updates, and status reports from this meeting transcript. Return as a JSON array of strings:',
    positive_feedback: 'Identify all positive feedback, achievements, successes, and progress mentioned in this meeting. Return as a JSON array of strings:',
    risks: 'Identify all risks, concerns, blockers, issues, and negative feedback mentioned in this meeting. Return as a JSON array of strings:',
    action_items: 'Extract all action items, follow-ups, tasks, and commitments made during this meeting. Include who is responsible if mentioned. Return as a JSON array of strings:',
  };

  for (const [category, prompt] of Object.entries(insightPrompts)) {
    const response = await ai.run('@cf/meta/llama-2-7b-chat-int8', {
      prompt: `${prompt}\n\nProject: ${meeting.project_title}\n\n${fullText}`,
      max_tokens: 300,
    });

    let insights = [];
    try {
      insights = JSON.parse(response.response);
    } catch {
      // Fallback: split by newlines if not valid JSON
      insights = response.response
        .split('\n')
        .filter((line: string) => line.trim().length > 0)
        .map((line: string) => line.replace(/^[-*]\s*/, '').trim());
    }

    // Store each insight
    for (const insightText of insights) {
      if (insightText && insightText.length > 10) { // Filter out very short insights
        await env.DB.prepare(`
          INSERT INTO project_insights (
            id, project_id, meeting_id, category, text,
            confidence_score, metadata, created_at
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `).bind(
          crypto.randomUUID(),
          projectId,
          meetingId,
          category,
          insightText,
          0.8, // Default confidence
          JSON.stringify({
            projectTitle: meeting.project_title,
            meetingDate: meeting.date,
          }),
          new Date().toISOString()
        ).run();
      }
    }
  }

  // Mark meeting as insights generated
  await env.DB.prepare(
    'UPDATE meetings SET insight_generated = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?'
  ).bind(meetingId).run();

  console.log(`Insights generation complete for meeting ${meetingId}`);
}

async function extractTasks(meetingId: string, env: Env): Promise<void> {
  const ai = new Ai(env.AI);
  
  // Fetch action items from insights
  const actionItems = await env.DB.prepare(`
    SELECT pi.*, m.date as meeting_date
    FROM project_insights pi
    JOIN meetings m ON pi.meeting_id = m.id
    WHERE pi.meeting_id = ? AND pi.category = 'action_items'
  `).bind(meetingId).all();

  if (actionItems.results.length === 0) {
    console.log(`No action items found for meeting ${meetingId}`);
    return;
  }

  // Process each action item to extract structured task information
  for (const item of actionItems.results) {
    const taskText = item.text as string;
    
    // Extract task details using AI
    const response = await ai.run('@cf/meta/llama-2-7b-chat-int8', {
      prompt: `Extract task information from this action item. Return JSON with fields: description, assigned_to (name or null), due_date (YYYY-MM-DD or null), priority (low/medium/high/critical).

Action item: ${taskText}
Meeting date: ${item.meeting_date}

JSON:`,
      max_tokens: 150,
    });

    let taskData;
    try {
      taskData = JSON.parse(response.response);
    } catch {
      // Fallback to basic extraction
      taskData = {
        description: taskText,
        assigned_to: extractAssignee(taskText),
        due_date: extractDueDate(taskText, item.meeting_date as string),
        priority: extractPriority(taskText),
      };
    }

    // Insert task
    await env.DB.prepare(`
      INSERT INTO project_tasks (
        id, project_id, meeting_id, task_description,
        assigned_to, due_date, status, priority,
        source_chunk_id, confidence_score, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      crypto.randomUUID(),
      item.project_id,
      meetingId,
      taskData.description || taskText,
      taskData.assigned_to,
      taskData.due_date,
      'pending',
      taskData.priority || 'medium',
      null, // We could link to specific chunk if needed
      0.7, // Confidence score
      new Date().toISOString()
    ).run();
  }

  console.log(`Task extraction complete for meeting ${meetingId}`);
}

// Helper functions for fallback task extraction
function extractAssignee(text: string): string | null {
  const patterns = [
    /(\w+)\s+will\s+/i,
    /assigned\s+to\s+(\w+)/i,
    /(\w+)\s+to\s+take\s+care/i,
    /(\w+)\s+owns\s+this/i,
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      return match[1];
    }
  }
  
  return null;
}

function extractDueDate(text: string, meetingDate: string): string | null {
  const patterns = [
    /by\s+(\d{1,2}\/\d{1,2}\/\d{2,4})/i,
    /due\s+(\d{1,2}\/\d{1,2}\/\d{2,4})/i,
    /before\s+(\d{1,2}\/\d{1,2}\/\d{2,4})/i,
    /by\s+(next\s+\w+)/i,
    /by\s+(end\s+of\s+\w+)/i,
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      // Convert relative dates
      if (match[1].includes('next')) {
        const meetingDateObj = new Date(meetingDate);
        meetingDateObj.setDate(meetingDateObj.getDate() + 7);
        return meetingDateObj.toISOString().split('T')[0];
      }
      return match[1]; // Assume proper date format
    }
  }
  
  return null;
}

function extractPriority(text: string): string {
  const high = /urgent|critical|asap|immediately|high\s+priority/i;
  const low = /low\s+priority|when\s+possible|eventually/i;
  
  if (high.test(text)) return 'high';
  if (low.test(text)) return 'low';
  return 'medium';
}