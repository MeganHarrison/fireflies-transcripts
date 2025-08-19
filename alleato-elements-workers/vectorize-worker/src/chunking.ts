import { TranscriptSentence, TextChunk } from './types';

export class TranscriptChunker {
  private maxChunkSize: number;
  private overlapSize: number;
  private maxTimeGap: number;

  constructor(
    maxChunkSize: number = 1000, // characters
    overlapSize: number = 200,   // characters
    maxTimeGap: number = 30000   // 30 seconds in milliseconds
  ) {
    this.maxChunkSize = maxChunkSize;
    this.overlapSize = overlapSize;
    this.maxTimeGap = maxTimeGap;
  }

  /**
   * Create semantic chunks from transcript sentences
   * Chunks are created based on:
   * 1. Size constraints
   * 2. Time gaps between sentences
   * 3. Speaker changes (tries to keep same speaker together)
   */
  createChunks(sentences: TranscriptSentence[]): TextChunk[] {
    if (!sentences || sentences.length === 0) {
      return [];
    }

    const chunks: TextChunk[] = [];
    let currentChunk: TextChunk = this.initializeChunk();
    let lastEndTime = 0;

    for (let i = 0; i < sentences.length; i++) {
      const sentence = sentences[i];
      const timeGap = sentence.start_time - lastEndTime;
      
      // Check if we should start a new chunk
      const shouldStartNewChunk = 
        currentChunk.text.length > 0 && (
          // Size limit reached
          currentChunk.text.length + sentence.text.length > this.maxChunkSize ||
          // Large time gap
          timeGap > this.maxTimeGap ||
          // Natural break point (e.g., question followed by long answer)
          this.isNaturalBreakPoint(sentences, i)
        );

      if (shouldStartNewChunk) {
        chunks.push(currentChunk);
        
        // Create overlap with previous chunk
        const overlapText = this.getOverlapText(currentChunk.text);
        currentChunk = this.initializeChunk();
        
        if (overlapText) {
          currentChunk.text = overlapText + ' ';
        }
      }

      // Add sentence to current chunk
      if (currentChunk.text.length > 0) {
        currentChunk.text += ' ';
      }
      currentChunk.text += sentence.text;
      currentChunk.speakers.add(sentence.speaker_name);
      currentChunk.sentenceCount++;
      
      // Update time bounds
      if (currentChunk.startTime === 0) {
        currentChunk.startTime = sentence.start_time;
      }
      currentChunk.endTime = sentence.end_time;
      lastEndTime = sentence.end_time;
    }

    // Add the last chunk
    if (currentChunk.text.length > 0) {
      chunks.push(currentChunk);
    }

    return chunks;
  }

  private initializeChunk(): TextChunk {
    return {
      text: '',
      startTime: 0,
      endTime: 0,
      speakers: new Set<string>(),
      sentenceCount: 0,
    };
  }

  private getOverlapText(text: string): string {
    if (text.length <= this.overlapSize) {
      return text;
    }
    
    // Try to find a sentence boundary for cleaner overlap
    const targetStart = text.length - this.overlapSize;
    const substring = text.substring(targetStart);
    
    // Look for sentence start (capital letter after period)
    const sentenceStart = substring.search(/\.\s+[A-Z]/);
    if (sentenceStart > 0) {
      return substring.substring(sentenceStart + 2); // Skip period and space
    }
    
    return substring;
  }

  private isNaturalBreakPoint(sentences: TranscriptSentence[], index: number): boolean {
    if (index === 0 || index >= sentences.length - 1) {
      return false;
    }

    const current = sentences[index];
    const previous = sentences[index - 1];
    const next = sentences[index + 1];

    // Check for topic transitions
    const isQuestion = current.text.trim().endsWith('?');
    const speakerChange = current.speaker_name !== next.speaker_name;
    
    // Natural break: question followed by different speaker
    if (isQuestion && speakerChange) {
      return true;
    }

    // Natural break: long monologue ending
    if (current.speaker_name === previous.speaker_name && 
        current.speaker_name !== next.speaker_name &&
        current.end_time - previous.start_time > 60000) { // 1 minute monologue
      return true;
    }

    return false;
  }

  /**
   * Create a summary chunk that represents the entire transcript
   */
  createSummaryChunk(sentences: TranscriptSentence[], summary?: string): TextChunk {
    const allSpeakers = new Set<string>();
    let totalDuration = 0;
    
    if (sentences.length > 0) {
      totalDuration = sentences[sentences.length - 1].end_time - sentences[0].start_time;
      sentences.forEach(s => allSpeakers.add(s.speaker_name));
    }

    const chunk: TextChunk = {
      text: summary || this.generateQuickSummary(sentences),
      startTime: sentences[0]?.start_time || 0,
      endTime: sentences[sentences.length - 1]?.end_time || 0,
      speakers: allSpeakers,
      sentenceCount: sentences.length,
    };

    return chunk;
  }

  private generateQuickSummary(sentences: TranscriptSentence[]): string {
    if (sentences.length === 0) {
      return 'Empty transcript';
    }

    // Take first and last few sentences as a basic summary
    const firstSentences = sentences.slice(0, 3).map(s => s.text).join(' ');
    const lastSentences = sentences.slice(-2).map(s => s.text).join(' ');
    
    return `Meeting start: ${firstSentences} ... Meeting end: ${lastSentences}`;
  }
}