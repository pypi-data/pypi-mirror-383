import type { Chunk, MemoryEntry } from '../types.js';

export class SmartChunker {
  private chunkSize: number;
  private overlap: number;

  constructor(chunkSize = 512, overlap = 50) {
    this.chunkSize = chunkSize;
    this.overlap = overlap;
  }

  async chunkMemory(memory: MemoryEntry, previousContext?: string, nextContext?: string): Promise<Omit<Chunk, 'id' | 'embedding'>[]> {
    const sentences = this.splitIntoSentences(memory.content);
    const chunks: Omit<Chunk, 'id' | 'embedding'>[] = [];
    
    let currentChunk: string[] = [];
    let currentLength = 0;
    let position = 0;

    for (let i = 0; i < sentences.length; i++) {
      const sentence = sentences[i];
      const sentenceLength = sentence.length;

      if (currentLength + sentenceLength > this.chunkSize && currentChunk.length > 0) {
        // Create chunk with contextual information
        const chunkContent = currentChunk.join(' ');
        const contextualContent = this.addContext(chunkContent, memory, previousContext, nextContext);
        
        chunks.push({
          memoryId: memory.id,
          content: chunkContent,
          contextualContent,
          position: position++,
          metadata: {
            userId: memory.userId,
            platform: memory.platform,
            conversationId: memory.conversationId,
            role: memory.role,
            timestamp: memory.timestamp.toISOString(),
            sentenceCount: currentChunk.length
          }
        });

        // Keep overlap
        const overlapSentences = Math.ceil(this.overlap / (this.chunkSize / currentChunk.length));
        currentChunk = currentChunk.slice(-overlapSentences);
        currentLength = currentChunk.join(' ').length;
      }

      currentChunk.push(sentence);
      currentLength += sentenceLength + 1;
    }

    // Add remaining chunk
    if (currentChunk.length > 0) {
      const chunkContent = currentChunk.join(' ');
      const contextualContent = this.addContext(chunkContent, memory, previousContext, nextContext);
      
      chunks.push({
        memoryId: memory.id,
        content: chunkContent,
        contextualContent,
        position: position++,
        metadata: {
          userId: memory.userId,
          platform: memory.platform,
          conversationId: memory.conversationId,
          role: memory.role,
          timestamp: memory.timestamp.toISOString(),
          sentenceCount: currentChunk.length
        }
      });
    }

    return chunks;
  }

  private addContext(content: string, memory: MemoryEntry, previousContext?: string, nextContext?: string): string {
    // Anthropic's contextual retrieval approach
    const contextParts = [
      `Platform: ${memory.platform}`,
      `Role: ${memory.role}`,
      `Conversation: ${memory.conversationId}`,
      previousContext ? `Previous: ${previousContext.slice(-100)}` : null,
      `Content: ${content}`,
      nextContext ? `Next: ${nextContext.slice(0, 100)}` : null
    ].filter(Boolean);

    return contextParts.join('\n');
  }

  private splitIntoSentences(text: string): string[] {
    // Smart sentence splitting that handles common abbreviations
    const sentences = text
      .replace(/([.!?])\s+(?=[A-Z])/g, '$1|')
      .split('|')
      .map(s => s.trim())
      .filter(s => s.length > 0);

    return sentences;
  }

  // Semantic chunking based on topic shifts
  async semanticChunk(memory: MemoryEntry, embeddings: number[][]): Promise<Omit<Chunk, 'id' | 'embedding'>[]> {
    const sentences = this.splitIntoSentences(memory.content);
    
    if (sentences.length <= 1 || embeddings.length !== sentences.length) {
      return this.chunkMemory(memory);
    }

    // Find topic boundaries using cosine similarity between consecutive sentences
    const boundaries: number[] = [0];
    const threshold = 0.7; // Similarity threshold for topic shift

    for (let i = 0; i < embeddings.length - 1; i++) {
      const similarity = this.cosineSimilarity(embeddings[i], embeddings[i + 1]);
      if (similarity < threshold) {
        boundaries.push(i + 1);
      }
    }
    boundaries.push(sentences.length);

    // Create chunks based on boundaries
    const chunks: Omit<Chunk, 'id' | 'embedding'>[] = [];
    for (let i = 0; i < boundaries.length - 1; i++) {
      const start = boundaries[i];
      const end = boundaries[i + 1];
      const chunkSentences = sentences.slice(start, end);
      const content = chunkSentences.join(' ');

      chunks.push({
        memoryId: memory.id,
        content,
        contextualContent: this.addContext(content, memory),
        position: i,
        metadata: {
          userId: memory.userId,
          platform: memory.platform,
          conversationId: memory.conversationId,
          role: memory.role,
          timestamp: memory.timestamp.toISOString(),
          sentenceCount: chunkSentences.length,
          semanticBoundary: true
        }
      });
    }

    return chunks;
  }

  private cosineSimilarity(a: number[], b: number[]): number {
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }

    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }
}
