import { FirefliesTranscript } from './types';

export class FirefliesAPI {
  private apiKey: string;
  private apiUrl: string;

  constructor(apiKey: string, apiUrl: string = 'https://api.fireflies.ai/graphql') {
    this.apiKey = apiKey;
    this.apiUrl = apiUrl;
  }

  async getTranscripts(since?: string, limit: number = 50): Promise<FirefliesTranscript[]> {
    const query = `
      query GetTranscripts($limit: Int!, $since: String) {
        transcripts(limit: $limit, since: $since) {
          id
          title
          date
          duration
          participants
          organizer_email
          meeting_url
          audio_url
          video_url
          transcript_url
          sentences {
            text
            speaker_name
            speaker_email
            start_time
            end_time
          }
          summary
        }
      }
    `;

    const variables = {
      limit,
      since: since || new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString() // Default to last 24 hours
    };

    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`,
        },
        body: JSON.stringify({ query, variables }),
      });

      if (!response.ok) {
        throw new Error(`Fireflies API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.errors) {
        throw new Error(`GraphQL errors: ${JSON.stringify(data.errors)}`);
      }

      return data.data.transcripts || [];
    } catch (error) {
      console.error('Error fetching transcripts from Fireflies:', error);
      throw error;
    }
  }

  async getTranscriptById(id: string): Promise<FirefliesTranscript | null> {
    const query = `
      query GetTranscript($id: String!) {
        transcript(id: $id) {
          id
          title
          date
          duration
          participants
          organizer_email
          meeting_url
          audio_url
          video_url
          transcript_url
          sentences {
            text
            speaker_name
            speaker_email
            start_time
            end_time
          }
          summary
        }
      }
    `;

    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`,
        },
        body: JSON.stringify({ query, variables: { id } }),
      });

      if (!response.ok) {
        throw new Error(`Fireflies API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.errors) {
        throw new Error(`GraphQL errors: ${JSON.stringify(data.errors)}`);
      }

      return data.data.transcript || null;
    } catch (error) {
      console.error('Error fetching transcript from Fireflies:', error);
      throw error;
    }
  }

  async downloadTranscriptFile(transcriptUrl: string): Promise<string> {
    try {
      const response = await fetch(transcriptUrl, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to download transcript: ${response.status}`);
      }

      return await response.text();
    } catch (error) {
      console.error('Error downloading transcript file:', error);
      throw error;
    }
  }
}