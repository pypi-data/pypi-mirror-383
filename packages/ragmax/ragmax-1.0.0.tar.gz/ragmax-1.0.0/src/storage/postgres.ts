import pg from 'pg';
import type { MemoryEntry, Chunk } from '../types.js';

const { Pool } = pg;

export class PostgresStorage {
  private pool: pg.Pool;

  constructor() {
    this.pool = new Pool({
      host: process.env.POSTGRES_HOST || 'localhost',
      port: parseInt(process.env.POSTGRES_PORT || '5432'),
      database: process.env.POSTGRES_DB || 'ai_memory',
      user: process.env.POSTGRES_USER || 'postgres',
      password: process.env.POSTGRES_PASSWORD || 'postgres',
    });
  }

  async saveMemory(entry: Omit<MemoryEntry, 'id'>): Promise<MemoryEntry> {
    const result = await this.pool.query(
      `INSERT INTO memory_entries (user_id, platform, conversation_id, content, role, timestamp, metadata)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING *`,
      [entry.userId, entry.platform, entry.conversationId, entry.content, entry.role, entry.timestamp, entry.metadata]
    );
    return this.rowToMemoryEntry(result.rows[0]);
  }

  async saveChunks(chunks: Omit<Chunk, 'id'>[]): Promise<Chunk[]> {
    const client = await this.pool.connect();
    try {
      await client.query('BEGIN');
      const savedChunks: Chunk[] = [];

      for (const chunk of chunks) {
        const result = await client.query(
          `INSERT INTO chunks (memory_id, content, contextual_content, embedding, position, metadata)
           VALUES ($1, $2, $3, $4, $5, $6)
           RETURNING *`,
          [chunk.memoryId, chunk.content, chunk.contextualContent, chunk.embedding ? `[${chunk.embedding.join(',')}]` : null, chunk.position, chunk.metadata]
        );
        savedChunks.push(this.rowToChunk(result.rows[0]));
      }

      await client.query('COMMIT');
      return savedChunks;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  async searchByVector(embedding: number[], userId: string, limit: number = 10): Promise<Array<{ chunk: Chunk; score: number; memory: MemoryEntry }>> {
    const result = await this.pool.query(
      `SELECT 
        c.*,
        m.*,
        1 - (c.embedding <=> $1::vector) as similarity
       FROM chunks c
       JOIN memory_entries m ON c.memory_id = m.id
       WHERE m.user_id = $2 AND c.embedding IS NOT NULL
       ORDER BY c.embedding <=> $1::vector
       LIMIT $3`,
      [`[${embedding.join(',')}]`, userId, limit]
    );

    return result.rows.map(row => ({
      chunk: this.rowToChunk(row),
      score: row.similarity,
      memory: this.rowToMemoryEntry(row)
    }));
  }

  async getRecentMemories(userId: string, limit: number = 20): Promise<MemoryEntry[]> {
    const result = await this.pool.query(
      `SELECT * FROM memory_entries
       WHERE user_id = $1
       ORDER BY timestamp DESC
       LIMIT $2`,
      [userId, limit]
    );
    return result.rows.map(this.rowToMemoryEntry);
  }

  private rowToMemoryEntry(row: any): MemoryEntry {
    return {
      id: row.id,
      userId: row.user_id,
      platform: row.platform,
      conversationId: row.conversation_id,
      content: row.content,
      role: row.role,
      timestamp: row.timestamp,
      metadata: row.metadata || {}
    };
  }

  private rowToChunk(row: any): Chunk {
    return {
      id: row.id,
      memoryId: row.memory_id,
      content: row.content,
      contextualContent: row.contextual_content,
      embedding: row.embedding,
      position: row.position,
      metadata: row.metadata || {}
    };
  }

  async close(): Promise<void> {
    await this.pool.end();
  }
}
