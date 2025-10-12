import { createClient } from 'redis';
import type { MemoryEntry } from '../types.js';

export class RedisCache {
  private client: ReturnType<typeof createClient>;
  private ttl: number;

  constructor() {
    this.client = createClient({
      socket: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379')
      },
      password: process.env.REDIS_PASSWORD || undefined
    });
    this.ttl = parseInt(process.env.HOT_MEMORY_TTL || '3600');
  }

  async connect(): Promise<void> {
    await this.client.connect();
  }

  async cacheMemory(userId: string, memory: MemoryEntry): Promise<void> {
    const key = `hot:${userId}:${memory.conversationId}`;
    await this.client.lPush(key, JSON.stringify(memory));
    await this.client.expire(key, this.ttl);
    await this.client.lTrim(key, 0, 49); // Keep last 50 messages
  }

  async getHotMemory(userId: string, conversationId: string): Promise<MemoryEntry[]> {
    const key = `hot:${userId}:${conversationId}`;
    const data = await this.client.lRange(key, 0, -1);
    return data.map(item => JSON.parse(item));
  }

  async cacheSearchResults(query: string, userId: string, results: any[]): Promise<void> {
    const key = `search:${userId}:${this.hashQuery(query)}`;
    await this.client.setEx(key, 300, JSON.stringify(results)); // 5 min cache
  }

  async getCachedSearch(query: string, userId: string): Promise<any[] | null> {
    const key = `search:${userId}:${this.hashQuery(query)}`;
    const data = await this.client.get(key);
    return data ? JSON.parse(data) : null;
  }

  private hashQuery(query: string): string {
    // Simple hash for cache key
    let hash = 0;
    for (let i = 0; i < query.length; i++) {
      hash = ((hash << 5) - hash) + query.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(36);
  }

  async close(): Promise<void> {
    await this.client.quit();
  }
}
