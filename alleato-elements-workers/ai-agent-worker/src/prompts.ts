import { ProjectContext, RetrievedChunk } from './types';

export function buildSystemPrompt(mode: 'recall' | 'strategy' | 'balanced' = 'balanced'): string {
  const basePrompt = `You are an AI Project Manager and Business Strategist with access to meeting transcripts and project data. Your role is to provide intelligent, contextual assistance based on the information retrieved from the knowledge base.`;

  const modePrompts = {
    recall: `
${basePrompt}

Focus on FACTUAL RECALL:
- Provide accurate information from meeting transcripts
- Quote specific discussions when relevant
- Clarify who said what and when
- Summarize key decisions and outcomes
- Stay strictly within the provided context`,

    strategy: `
${basePrompt}

Focus on STRATEGIC INSIGHTS:
- Identify patterns across meetings and projects
- Provide high-level recommendations
- Spot risks and opportunities
- Suggest process improvements
- Connect dots between different discussions
- Think beyond individual meetings to see the bigger picture`,

    balanced: `
${basePrompt}

Balance RECALL and STRATEGY:
- Ground insights in specific meeting data
- Provide both tactical and strategic guidance
- Reference specific discussions while drawing broader conclusions
- Help with immediate needs while considering long-term implications`,
  };

  return modePrompts[mode];
}

export function formatContext(
  chunks: RetrievedChunk[],
  projectContext?: ProjectContext
): string {
  let context = '';

  // Add retrieved chunks
  if (chunks.length > 0) {
    context += 'RELEVANT MEETING EXCERPTS:\n\n';
    
    for (const chunk of chunks) {
      context += `[${chunk.metadata?.meetingTitle || 'Meeting'} - ${chunk.metadata?.meetingDate || 'Date unknown'}]\n`;
      if (chunk.metadata?.speakers?.length > 0) {
        context += `Speakers: ${chunk.metadata.speakers.join(', ')}\n`;
      }
      context += `${chunk.text}\n\n`;
    }
  }

  // Add project context
  if (projectContext?.project) {
    context += '\nPROJECT CONTEXT:\n';
    context += `Project: ${projectContext.project.title}\n`;
    context += `Status: ${projectContext.project.status}\n`;
    
    if (projectContext.activeTasks.length > 0) {
      context += '\nActive Tasks:\n';
      for (const task of projectContext.activeTasks) {
        context += `- [${task.priority}] ${task.description}`;
        if (task.assignedTo) context += ` (${task.assignedTo})`;
        if (task.dueDate) context += ` - Due: ${task.dueDate}`;
        context += '\n';
      }
    }

    if (projectContext.recentInsights.length > 0) {
      context += '\nRecent Insights:\n';
      for (const insight of projectContext.recentInsights) {
        context += `- [${insight.category}] ${insight.text}\n`;
      }
    }

    context += `\nProject Sentiment: ${projectContext.sentiment.current > 0 ? 'Positive' : 'Negative'} (${projectContext.sentiment.trend})\n`;
  }

  return context;
}

export function generateFollowUpQuestions(
  query: string,
  chunks: RetrievedChunk[],
  projectContext?: ProjectContext
): string[] {
  const questions: string[] = [];

  // Based on retrieved content
  if (chunks.length > 0) {
    const hasActionItems = chunks.some(c => 
      c.text.toLowerCase().includes('action') || 
      c.text.toLowerCase().includes('todo')
    );
    
    if (hasActionItems) {
      questions.push('What are the specific deadlines for these action items?');
      questions.push('Who should I follow up with about task progress?');
    }

    const hasRisks = chunks.some(c => 
      c.text.toLowerCase().includes('risk') || 
      c.text.toLowerCase().includes('concern') ||
      c.text.toLowerCase().includes('issue')
    );
    
    if (hasRisks) {
      questions.push('What mitigation strategies were discussed for these risks?');
      questions.push('Have these issues been resolved in subsequent meetings?');
    }
  }

  // Based on project context
  if (projectContext?.project) {
    if (projectContext.sentiment.trend === 'declining') {
      questions.push('What factors are contributing to the negative trend?');
      questions.push('What actions can we take to improve project morale?');
    }

    if (projectContext.activeTasks.filter(t => t.priority === 'critical').length > 0) {
      questions.push('What support do we need for critical tasks?');
      questions.push('Should we reprioritize other work to focus on critical items?');
    }
  }

  // General strategic questions
  questions.push('How does this compare to similar projects?');
  questions.push('What lessons can we apply to future initiatives?');

  return questions.slice(0, 3); // Return top 3 most relevant
}

export function formatResponse(
  answer: string,
  chunks: RetrievedChunk[],
  followUpQuestions: string[],
  mode: string
): string {
  let formattedResponse = answer;

  // Add source references
  if (chunks.length > 0) {
    formattedResponse += '\n\n---\n**Sources:**\n';
    const uniqueMeetings = new Map<string, any>();
    
    for (const chunk of chunks) {
      if (!uniqueMeetings.has(chunk.meetingId)) {
        uniqueMeetings.set(chunk.meetingId, {
          title: chunk.metadata?.meetingTitle || 'Meeting',
          date: chunk.metadata?.meetingDate || 'Date unknown',
        });
      }
    }

    for (const [id, meeting] of uniqueMeetings) {
      formattedResponse += `- ${meeting.title} (${meeting.date})\n`;
    }
  }

  // Add follow-up questions
  if (followUpQuestions.length > 0) {
    formattedResponse += '\n**You might also want to know:**\n';
    for (const question of followUpQuestions) {
      formattedResponse += `- ${question}\n`;
    }
  }

  return formattedResponse;
}