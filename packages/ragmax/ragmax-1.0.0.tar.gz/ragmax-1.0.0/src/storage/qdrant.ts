import { QdrantClient } from '@qdrant/js-client-rest';
import type { Chunk } from '../types.js';

export class QdrantStorage {
  private client: QdrantClient;
  private collectionName = 'memory_chunks';

  constructor() {
    this.client = new QdrantClient({
      url: process.env.QDRANT_URL || 'http://localhost:6333',
      apiKey: process.env.QDRANT_API_KEY
    });
  }

  async initialize(): Promise<void> {
    try {
      await this.client.getCollection(this.collectionName);
    } catch {
      await this.client.createCollection(this.collectionName, {
        vectors: {
          size: 1024, // Voyage AI / Cohere dimension
          distance: 'Cosine'
        },
        optimizers_config: {
          indexing_threshold: 10000
        }
      });

      // Create payload indexes for filtering
      await this.client.createPayloadIndex(this.collectionName, {
        field_name: 'userId',
        field_schema: 'keyword'
      });
      await this.client.createPayloadIndex(this.collectionName, {
        field_name: 'platform',
        field_schema: 'keyword'
      });
      await this.client.createPayloadIndex(this.collectionName, {
        field_name: 'timestamp',
        field_schema: 'integer'
      });
    }
  }

  async upsertChunks(chunks: Chunk[]): Promise<void> {
    const points = chunks.map(chunk => ({
      id: chunk.id,
      vector: chunk.embedding!,
      payload: {
        memoryId: chunk.memoryId,
        content: chunk.content,
        contextualContent: chunk.contextualContent,
        position: chunk.position,
        metadata: chunk.metadata
      }
    }));

    await this.client.upsert(this.collectionName, {
      wait: true,
      points
    });
  }

  async search(embedding: number[], userId: string, limit: number = 10, filter?: any) {
    try {
      const searchFilter: any = {
        must: [{ key: 'metadata.userId', match: { value: userId } }]
      };

      if (filter?.platform) {
        searchFilter.must.push({ key: 'metadata.platform', match: { value: filter.platform } });
      }

      const results = await this.client.search(this.collectionName, {
        vector: embedding,
        filter: searchFilter,
        limit,
        with_payload: true
      });

      return results || [];
    } catch (error) {
      console.error('Qdrant search error:', error);
      return [];
    }
  }
}
