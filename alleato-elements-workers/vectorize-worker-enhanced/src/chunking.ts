// Intelligent chunking strategies for transcript processing

import { ChunkingOptions } from '../../shared/types';

export interface TranscriptSentence {
  speaker_id: string;
  speaker_name: string;
  text: string;
  start_time: number;
  end_time: number;
}

export interface ProcessedChunk {
  content: string;
  startTime: number;
  endTime: number;
  speakers: Set<string>;
  sentenceCount: number;
  tokenCount: number;
}

export class TranscriptChunker {
  private options: ChunkingOptions;

  constructor(options: ChunkingOptions) {
    this.options = options;
  }

  async chunkTranscript(sentences: TranscriptSentence[]): Promise<ProcessedChunk[]> {
    switch (this.options.method) {
      case 'sentence':
        return this.sentenceBasedChunking(sentences);
      case 'semantic':
        return this.semanticChunking(sentences);
      case 'sliding_window':
        return this.slidingWindowChunking(sentences);
      default:
        throw new Error(`Unknown chunking method: ${this.options.method}`);
    }
  }

  private sentenceBasedChunking(sentences: TranscriptSentence[]): ProcessedChunk[] {
    const chunks: ProcessedChunk[] = [];
    let currentChunk: TranscriptSentence[] = [];
    let currentTokens = 0;

    for (let i = 0; i < sentences.length; i++) {
      const sentence = sentences[i];
      const sentenceTokens = this.estimateTokens(sentence.text);

      // Check if adding this sentence would exceed chunk size
      if (currentTokens + sentenceTokens > this.options.chunkSize && currentChunk.length > 0) {
        // Save current chunk
        chunks.push(this.createChunk(currentChunk));

        // Start new chunk with overlap
        if (this.options.overlap > 0) {
          const overlapSentences = this.getOverlapSentences(currentChunk, this.options.overlap);
          currentChunk = [...overlapSentences];
          currentTokens = overlapSentences.reduce((sum, s) => sum + this.estimateTokens(s.text), 0);
        } else {
          currentChunk = [];
          currentTokens = 0;
        }
      }

      // Check speaker boundary preservation
      if (this.options.preserveSpeakerBoundaries && 
          currentChunk.length > 0 && 
          currentChunk[currentChunk.length - 1].speaker_id !== sentence.speaker_id &&
          currentTokens + sentenceTokens > this.options.chunkSize * 0.8) {
        // Close chunk at speaker boundary
        chunks.push(this.createChunk(currentChunk));
        currentChunk = [];
        currentTokens = 0;
      }

      currentChunk.push(sentence);
      currentTokens += sentenceTokens;
    }

    // Add final chunk
    if (currentChunk.length > 0) {
      chunks.push(this.createChunk(currentChunk));
    }

    return chunks;
  }

  private semanticChunking(sentences: TranscriptSentence[]): ProcessedChunk[] {
    // Semantic chunking groups sentences by topic coherence
    const chunks: ProcessedChunk[] = [];
    let currentChunk: TranscriptSentence[] = [];
    let currentTokens = 0;
    let lastSpeaker = '';

    for (let i = 0; i < sentences.length; i++) {
      const sentence = sentences[i];
      const sentenceTokens = this.estimateTokens(sentence.text);

      // Detect topic boundaries (simple heuristic based on speaker changes and pause detection)
      const speakerChanged = lastSpeaker && lastSpeaker !== sentence.speaker_id;
      const longPause = i > 0 && (sentence.start_time - sentences[i - 1].end_time) > 5; // 5 second pause
      const topicBoundary = speakerChanged && longPause;

      if ((topicBoundary || currentTokens + sentenceTokens > this.options.chunkSize) && currentChunk.length > 0) {
        chunks.push(this.createChunk(currentChunk));

        // Handle overlap for semantic continuity
        if (this.options.overlap > 0 && !topicBoundary) {
          const overlapSentences = this.getOverlapSentences(currentChunk, this.options.overlap);
          currentChunk = [...overlapSentences];
          currentTokens = overlapSentences.reduce((sum, s) => sum + this.estimateTokens(s.text), 0);
        } else {
          currentChunk = [];
          currentTokens = 0;
        }
      }

      currentChunk.push(sentence);
      currentTokens += sentenceTokens;
      lastSpeaker = sentence.speaker_id;
    }

    if (currentChunk.length > 0) {
      chunks.push(this.createChunk(currentChunk));
    }

    return chunks;
  }

  private slidingWindowChunking(sentences: TranscriptSentence[]): ProcessedChunk[] {
    const chunks: ProcessedChunk[] = [];
    const stepSize = this.options.chunkSize - this.options.overlap;

    let startIdx = 0;
    while (startIdx < sentences.length) {
      const chunk: TranscriptSentence[] = [];
      let tokenCount = 0;
      let idx = startIdx;

      // Build chunk up to target size
      while (idx < sentences.length && tokenCount < this.options.chunkSize) {
        const sentence = sentences[idx];
        const sentenceTokens = this.estimateTokens(sentence.text);

        if (tokenCount + sentenceTokens <= this.options.chunkSize) {
          chunk.push(sentence);
          tokenCount += sentenceTokens;
          idx++;
        } else {
          break;
        }
      }

      if (chunk.length > 0) {
        chunks.push(this.createChunk(chunk));
      }

      // Move window
      startIdx += Math.max(1, Math.floor(chunk.length * (stepSize / this.options.chunkSize)));
    }

    return chunks;
  }

  private createChunk(sentences: TranscriptSentence[]): ProcessedChunk {
    const speakers = new Set(sentences.map(s => s.speaker_name));
    const content = sentences
      .map(s => `${s.speaker_name}: ${s.text}`)
      .join('\n');

    return {
      content,
      startTime: sentences[0].start_time,
      endTime: sentences[sentences.length - 1].end_time,
      speakers,
      sentenceCount: sentences.length,
      tokenCount: this.estimateTokens(content)
    };
  }

  private getOverlapSentences(chunk: TranscriptSentence[], overlapTokens: number): TranscriptSentence[] {
    const result: TranscriptSentence[] = [];
    let tokens = 0;

    // Work backwards from the end of the chunk
    for (let i = chunk.length - 1; i >= 0 && tokens < overlapTokens; i--) {
      result.unshift(chunk[i]);
      tokens += this.estimateTokens(chunk[i].text);
    }

    return result;
  }

  private estimateTokens(text: string): number {
    // Simple estimation: ~4 characters per token
    // In production, use tiktoken or the actual tokenizer
    return Math.ceil(text.length / 4);
  }
}

// Factory function for creating chunkers with predefined strategies
export function createChunker(strategy: 'balanced' | 'speaker_aware' | 'dense'): TranscriptChunker {
  const strategies: Record<string, ChunkingOptions> = {
    balanced: {
      method: 'sentence',
      chunkSize: 800,
      overlap: 200,
      preserveSpeakerBoundaries: true
    },
    speaker_aware: {
      method: 'semantic',
      chunkSize: 600,
      overlap: 150,
      preserveSpeakerBoundaries: true
    },
    dense: {
      method: 'sliding_window',
      chunkSize: 1000,
      overlap: 300,
      preserveSpeakerBoundaries: false
    }
  };

  return new TranscriptChunker(strategies[strategy]);
}