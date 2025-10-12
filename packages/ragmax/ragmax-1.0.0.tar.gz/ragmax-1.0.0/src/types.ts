export interface MemoryEntry {
  id: string;
  userId: string;
  platform: 'claude' | 'chatgpt' | 'gemini' | 'perplexity' | 'other';
  conversationId: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  metadata: Record<string, any>;
}

export interface Chunk {
  id: string;
  memoryId: string;
  content: string;
  contextualContent: string; // Content with surrounding context for better embeddings
  embedding?: number[];
  position: number;
  metadata: Record<string, any>;
}

export interface SearchResult {
  chunk: Chunk;
  score: number;
  relevance: number;
  memory: MemoryEntry;
}

export interface SearchOptions {
  query: string;
  userId: string;
  limit?: number;
  minScore?: number;
  platform?: string;
  timeRange?: {
    start: Date;
    end: Date;
  };
}

export interface AddMemoryOptions {
  userId: string;
  platform: string;
  conversationId: string;
  content: string;
  role: 'user' | 'assistant';
  metadata?: Record<string, any>;
}
