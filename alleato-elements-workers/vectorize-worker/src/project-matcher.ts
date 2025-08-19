import { Meeting, ProjectMatch } from './types';

export class ProjectMatcher {
  private projects: Map<string, ProjectInfo> = new Map();

  constructor(private db: D1Database) {}

  async loadProjects(): Promise<void> {
    const results = await this.db.prepare(`
      SELECT id, title, client_id, company_id, status_name
      FROM projects 
      WHERE deleted_at IS NULL
    `).all();

    this.projects.clear();
    for (const project of results.results) {
      this.projects.set(project.id as string, {
        id: project.id as string,
        title: project.title as string,
        clientId: project.client_id as string,
        companyId: project.company_id as string,
        status: project.status_name as string,
        keywords: this.extractKeywords(project.title as string),
      });
    }
  }

  async matchMeetingToProject(meeting: Meeting, transcriptText?: string): Promise<ProjectMatch | null> {
    const matches: ProjectMatch[] = [];

    // Load team members for participant matching
    const teamMembers = await this.loadTeamMembers();

    for (const [projectId, project] of this.projects) {
      let confidence = 0;
      const reasons: string[] = [];

      // 1. Title matching (40% weight)
      const titleMatch = this.calculateTitleMatch(meeting.title, project.title);
      if (titleMatch > 0) {
        confidence += titleMatch * 0.4;
        reasons.push(`Title match: ${Math.round(titleMatch * 100)}%`);
      }

      // 2. Participant matching (30% weight)
      const participants = JSON.parse(meeting.participants || '[]');
      const participantMatch = await this.calculateParticipantMatch(
        participants,
        projectId,
        teamMembers
      );
      if (participantMatch > 0) {
        confidence += participantMatch * 0.3;
        reasons.push(`Team member match: ${Math.round(participantMatch * 100)}%`);
      }

      // 3. Keyword matching in transcript (20% weight)
      if (transcriptText) {
        const keywordMatch = this.calculateKeywordMatch(transcriptText, project.keywords);
        if (keywordMatch > 0) {
          confidence += keywordMatch * 0.2;
          reasons.push(`Keyword match: ${Math.round(keywordMatch * 100)}%`);
        }
      }

      // 4. Existing project assignment (10% weight)
      if (meeting.project === projectId) {
        confidence += 0.1;
        reasons.push('Previously assigned to project');
      }

      if (confidence > 0) {
        matches.push({ projectId, confidence, reasons });
      }
    }

    // Sort by confidence and return best match
    matches.sort((a, b) => b.confidence - a.confidence);
    
    // Only return matches with reasonable confidence (> 30%)
    return matches.length > 0 && matches[0].confidence > 0.3 ? matches[0] : null;
  }

  private calculateTitleMatch(meetingTitle: string, projectTitle: string): number {
    const meetingWords = this.extractKeywords(meetingTitle);
    const projectWords = this.extractKeywords(projectTitle);
    
    if (meetingWords.size === 0 || projectWords.size === 0) {
      return 0;
    }

    let matches = 0;
    for (const word of meetingWords) {
      if (projectWords.has(word)) {
        matches++;
      }
    }

    // Also check for substring matches
    const lowerMeeting = meetingTitle.toLowerCase();
    const lowerProject = projectTitle.toLowerCase();
    
    if (lowerMeeting.includes(lowerProject) || lowerProject.includes(lowerMeeting)) {
      return 0.9; // High confidence for direct substring match
    }

    return matches / Math.max(meetingWords.size, projectWords.size);
  }

  private async calculateParticipantMatch(
    participants: string[],
    projectId: string,
    teamMembers: Map<string, Set<string>>
  ): number {
    const projectTeam = teamMembers.get(projectId);
    if (!projectTeam || projectTeam.size === 0 || participants.length === 0) {
      return 0;
    }

    let matches = 0;
    for (const participant of participants) {
      const participantLower = participant.toLowerCase();
      for (const teamMember of projectTeam) {
        if (participantLower.includes(teamMember.toLowerCase()) ||
            teamMember.toLowerCase().includes(participantLower)) {
          matches++;
          break;
        }
      }
    }

    return matches / participants.length;
  }

  private calculateKeywordMatch(text: string, keywords: Set<string>): number {
    if (keywords.size === 0) {
      return 0;
    }

    const textLower = text.toLowerCase();
    let matches = 0;
    
    for (const keyword of keywords) {
      // Count occurrences (logarithmic scale to prevent gaming)
      const occurrences = (textLower.match(new RegExp(keyword, 'g')) || []).length;
      if (occurrences > 0) {
        matches += Math.min(1, Math.log(occurrences + 1) / Math.log(10));
      }
    }

    return Math.min(1, matches / keywords.size);
  }

  private extractKeywords(text: string): Set<string> {
    // Remove common words and extract meaningful keywords
    const stopWords = new Set([
      'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
      'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
      'meeting', 'call', 'sync', 'standup', 'review', 'discussion'
    ]);

    const words = text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 2 && !stopWords.has(word));

    return new Set(words);
  }

  private async loadTeamMembers(): Promise<Map<string, Set<string>>> {
    // This would ideally load from a team members table
    // For now, we'll parse from meeting participants
    const teamMap = new Map<string, Set<string>>();
    
    const results = await this.db.prepare(`
      SELECT DISTINCT project, participants
      FROM meetings
      WHERE project IS NOT NULL AND participants IS NOT NULL
      LIMIT 100
    `).all();

    for (const row of results.results) {
      const projectId = row.project as string;
      const participants = JSON.parse(row.participants as string || '[]');
      
      if (!teamMap.has(projectId)) {
        teamMap.set(projectId, new Set());
      }
      
      const team = teamMap.get(projectId)!;
      participants.forEach((p: string) => team.add(p));
    }

    return teamMap;
  }
}

interface ProjectInfo {
  id: string;
  title: string;
  clientId: string;
  companyId: string;
  status: string;
  keywords: Set<string>;
}