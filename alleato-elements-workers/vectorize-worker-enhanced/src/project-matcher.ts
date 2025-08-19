// Project matching logic for automatic project assignment

import { Project, Meeting, ProjectMatchResult } from '../../shared/types';

export class ProjectMatcher {
  private projects: Project[];
  private confidenceThreshold: number;

  constructor(projects: Project[], confidenceThreshold: number = 0.7) {
    this.projects = projects;
    this.confidenceThreshold = confidenceThreshold;
  }

  async matchMeetingToProject(meeting: Meeting, transcriptContent?: string): Promise<ProjectMatchResult | null> {
    const scores: Map<string, { score: number; reasons: string[] }> = new Map();

    for (const project of this.projects) {
      let score = 0;
      const reasons: string[] = [];

      // 1. Title matching (weight: 0.4)
      const titleScore = this.matchTitle(meeting.title, project.name, project.keywords);
      if (titleScore > 0) {
        score += titleScore * 0.4;
        reasons.push(`Title match: ${(titleScore * 100).toFixed(0)}%`);
      }

      // 2. Participant matching (weight: 0.3)
      const participantScore = this.matchParticipants(meeting.participants, project.teamMembers);
      if (participantScore > 0) {
        score += participantScore * 0.3;
        reasons.push(`Team member match: ${(participantScore * 100).toFixed(0)}%`);
      }

      // 3. Content keyword matching (weight: 0.3)
      if (transcriptContent) {
        const contentScore = this.matchContent(transcriptContent, project.keywords);
        if (contentScore > 0) {
          score += contentScore * 0.3;
          reasons.push(`Content keywords: ${(contentScore * 100).toFixed(0)}%`);
        }
      }

      if (score > 0) {
        scores.set(project.id, { score, reasons });
      }
    }

    // Find best match
    let bestMatch: ProjectMatchResult | null = null;
    let highestScore = 0;

    for (const [projectId, { score, reasons }] of scores) {
      if (score > highestScore) {
        highestScore = score;
        bestMatch = {
          projectId,
          confidence: score,
          matchReasons: reasons
        };
      }
    }

    return bestMatch;
  }

  private matchTitle(meetingTitle: string, projectName: string, projectKeywords: string[]): number {
    const normalizedTitle = meetingTitle.toLowerCase();
    const normalizedProjectName = projectName.toLowerCase();

    // Direct project name match
    if (normalizedTitle.includes(normalizedProjectName)) {
      return 1.0;
    }

    // Check keywords in title
    let keywordMatches = 0;
    for (const keyword of projectKeywords) {
      if (normalizedTitle.includes(keyword.toLowerCase())) {
        keywordMatches++;
      }
    }

    return Math.min(keywordMatches / Math.max(projectKeywords.length, 1), 1.0);
  }

  private matchParticipants(meetingParticipants: any[], projectTeamMembers: string[]): number {
    if (!meetingParticipants || meetingParticipants.length === 0) {
      return 0;
    }

    let matches = 0;
    const normalizedTeamMembers = projectTeamMembers.map(m => m.toLowerCase());

    for (const participant of meetingParticipants) {
      const participantEmail = participant.email?.toLowerCase() || '';
      const participantName = participant.name?.toLowerCase() || '';

      for (const teamMember of normalizedTeamMembers) {
        if (participantEmail.includes(teamMember) || 
            participantName.includes(teamMember) ||
            teamMember.includes(participantEmail) ||
            teamMember.includes(participantName)) {
          matches++;
          break;
        }
      }
    }

    return matches / meetingParticipants.length;
  }

  private matchContent(content: string, keywords: string[]): number {
    if (!content || keywords.length === 0) {
      return 0;
    }

    const normalizedContent = content.toLowerCase();
    const wordCount = content.split(/\s+/).length;
    let keywordOccurrences = 0;

    for (const keyword of keywords) {
      const regex = new RegExp(`\\b${keyword.toLowerCase()}\\b`, 'g');
      const matches = normalizedContent.match(regex);
      if (matches) {
        keywordOccurrences += matches.length;
      }
    }

    // Normalize by content length to avoid bias toward longer transcripts
    const density = keywordOccurrences / Math.max(wordCount / 100, 1);
    
    // Cap at 1.0 and apply logarithmic scaling for better distribution
    return Math.min(Math.log(1 + density) / Math.log(10), 1.0);
  }

  determineProjectAssignment(matchResult: ProjectMatchResult | null): {
    projectId: string | null;
    needsReview: boolean;
    confidence: number;
  } {
    if (!matchResult) {
      return {
        projectId: null,
        needsReview: false,
        confidence: 0
      };
    }

    // High confidence: Auto-assign
    if (matchResult.confidence >= this.confidenceThreshold) {
      return {
        projectId: matchResult.projectId,
        needsReview: false,
        confidence: matchResult.confidence
      };
    }

    // Medium confidence: Assign but flag for review
    if (matchResult.confidence >= 0.4) {
      return {
        projectId: matchResult.projectId,
        needsReview: true,
        confidence: matchResult.confidence
      };
    }

    // Low confidence: Don't assign
    return {
      projectId: null,
      needsReview: false,
      confidence: matchResult.confidence
    };
  }
}