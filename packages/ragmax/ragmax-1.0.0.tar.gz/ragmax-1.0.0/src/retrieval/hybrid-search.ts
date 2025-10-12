import type { SearchResult, SearchOptions } from '../types.js';
import { PostgresStorage } from '../storage/postgres.js';
import { QdrantStorage } from '../storage/qdrant.js';
import { RedisCache } from '../storage/redis.js';
import { EmbeddingService } from '../services/embedding.js';
import { RerankerService } from '../services/reranker.js';

export class HybridSearch {
  private embeddings: EmbeddingService;
  private reranker: RerankerService;

  constructor(
    private postgres: PostgresStorage,
    private qdrant: QdrantStorage,
    private redis: RedisCache
  ) {
    this.embeddings = new EmbeddingService();
    this.reranker = new RerankerService();
  }

  async search(options: SearchOptions): Promise<SearchResult[]> {
    // Check cache first
    const cached = await this.redis.getCachedSearch(options.query, options.userId);
    if (cached) {
      return cached;
    }

    // Get query embedding (placeholder - will be replaced with actual embedding service)
    const queryEmbedding = await this.getEmbedding(options.query);

    // Parallel search across vector and keyword
    const [vectorResults, keywordResults] = await Promise.all([
      this.vectorSearch(queryEmbedding, options),
      this.keywordSearch(options)
    ]);

    // Merge and rerank results
    const merged = this.mergeResults(vectorResults, keywordResults);
    const reranked = await this.rerank(options.query, merged);

    // Apply filters
    const filtered = this.applyFilters(reranked, options);

    // Cache results
    await this.redis.cacheSearchResults(options.query, options.userId, filtered);

    return filtered.slice(0, options.limit || 10);
  }

  private async vectorSearch(embedding: number[], options: SearchOptions): Promise<SearchResult[]> {
    const results = await this.qdrant.search(
      embedding,
      options.userId,
      options.limit ? options.limit * 2 : 20,
      { platform: options.platform }
    );

    if (!results || results.length === 0) {
      return [];
    }

    return results.map(result => ({
      chunk: {
        id: result.id as string,
        memoryId: result.payload?.memoryId as string,
        content: result.payload?.content as string,
        contextualContent: result.payload?.contextualContent as string,
        position: result.payload?.position as number,
        metadata: result.payload?.metadata as Record<string, any>
      },
      score: result.score,
      relevance: result.score,
      memory: {} as any // Will be populated later
    }));
  }

  private async keywordSearch(options: SearchOptions): Promise<SearchResult[]> {
    // Placeholder for keyword search using PostgreSQL full-text search
    return [];
  }

  private mergeResults(vectorResults: SearchResult[], keywordResults: SearchResult[]): SearchResult[] {
    // Reciprocal Rank Fusion (RRF) for merging
    const k = 60;
    const scoreMap = new Map<string, { result: SearchResult; score: number }>();

    const addToMap = (results: SearchResult[], weight: number) => {
      results.forEach((result, rank) => {
        const id = result.chunk.id;
        const rrfScore = weight / (k + rank + 1);
        
        if (scoreMap.has(id)) {
          const existing = scoreMap.get(id)!;
          existing.score += rrfScore;
        } else {
          scoreMap.set(id, { result, score: rrfScore });
        }
      });
    };

    addToMap(vectorResults, 1.0);
    addToMap(keywordResults, 0.5);

    return Array.from(scoreMap.values())
      .sort((a, b) => b.score - a.score)
      .map(item => ({ ...item.result, score: item.score }));
  }

  private async rerank(query: string, results: SearchResult[]): Promise<SearchResult[]> {
    if (results.length === 0) return results;

    const documents = results.map(r => r.chunk.content);
    const reranked = await this.reranker.rerank(query, documents, Math.min(results.length, 20));

    if (!reranked || reranked.length === 0) {
      return results;
    }

    return reranked.map(item => ({
      ...results[item.index],
      relevance: item.relevanceScore
    }));
  }

  private applyFilters(results: SearchResult[], options: SearchOptions): SearchResult[] {
    let filtered = results;

    if (options.minScore) {
      filtered = filtered.filter(r => r.score >= options.minScore!);
    }

    if (options.timeRange) {
      filtered = filtered.filter(r => {
        const timestamp = new Date(r.chunk.metadata.timestamp);
        return timestamp >= options.timeRange!.start && timestamp <= options.timeRange!.end;
      });
    }

    return filtered;
  }

  private async getEmbedding(text: string): Promise<number[]> {
    return await this.embeddings.embed(text);
  }
}
