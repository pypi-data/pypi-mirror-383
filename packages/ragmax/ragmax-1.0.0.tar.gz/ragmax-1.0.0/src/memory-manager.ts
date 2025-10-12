import { PostgresStorage } from './storage/postgres.js';
import { RedisCache } from './storage/redis.js';
import { QdrantStorage } from './storage/qdrant.js';
import { SmartChunker } from './chunking/smart-chunker.js';
import { HybridSearch } from './retrieval/hybrid-search.js';
import { EmbeddingService } from './services/embedding.js';
import { IntelligenceService } from './services/intelligence.js';
import type { AddMemoryOptions, SearchOptions, SearchResult, MemoryEntry } from './types.js';

export class MemoryManager {
    private postgres: PostgresStorage;
    private redis: RedisCache;
    private qdrant: QdrantStorage;
    private chunker: SmartChunker;
    private search: HybridSearch;
    private embeddings: EmbeddingService;
    private intelligence: IntelligenceService;
    private useIntelligence: boolean;

    constructor() {
        this.postgres = new PostgresStorage();
        this.redis = new RedisCache();
        this.qdrant = new QdrantStorage();
        this.chunker = new SmartChunker(
            parseInt(process.env.CHUNK_SIZE || '512'),
            parseInt(process.env.CHUNK_OVERLAP || '50')
        );
        this.embeddings = new EmbeddingService();
        this.intelligence = new IntelligenceService();
        this.search = new HybridSearch(this.postgres, this.qdrant, this.redis);
        
        // Enable intelligent storage if configured
        this.useIntelligence = process.env.ENABLE_SMART_STORAGE === 'true';
    }

    async initialize(): Promise<void> {
        await Promise.all([
            this.redis.connect(),
            this.qdrant.initialize()
        ]);
    }

    async addMemory(options: AddMemoryOptions): Promise<MemoryEntry> {
        // Intelligent analysis (if enabled)
        if (this.useIntelligence && options.role === 'user') {
            const recentMemories = await this.postgres.getRecentMemories(options.userId, 3);
            const context = recentMemories.map(m => m.content);
            
            const analysis = await this.intelligence.analyzeContent(options.content, context);
            
            // Skip storage if not important
            if (!this.intelligence.shouldStoreMessage(analysis)) {
                console.log('Skipping storage - not important enough:', options.content.substring(0, 50));
                // Return a dummy memory (not stored)
                return {
                    id: 'skipped',
                    userId: options.userId,
                    platform: options.platform as any,
                    conversationId: options.conversationId,
                    content: options.content,
                    role: options.role,
                    timestamp: new Date(),
                    metadata: { skipped: true, analysis }
                };
            }
            
            // Enhance metadata with extracted info
            options.metadata = {
                ...options.metadata,
                facts: analysis.facts,
                preferences: analysis.preferences,
                context: analysis.context,
                importance: analysis.importance,
                summary: analysis.summary
            };
        }
        
        // Save to PostgreSQL (cold storage)
        const memory = await this.postgres.saveMemory({
            userId: options.userId,
            platform: options.platform as 'claude' | 'chatgpt' | 'gemini' | 'perplexity' | 'other',
            conversationId: options.conversationId,
            content: options.content,
            role: options.role,
            timestamp: new Date(),
            metadata: options.metadata || {}
        });

        // Cache in Redis (hot memory)
        await this.redis.cacheMemory(options.userId, memory);

        // Get recent context for better chunking
        const recentMemories = await this.postgres.getRecentMemories(options.userId, 5);
        const previousContext = recentMemories.length > 1 ? recentMemories[1].content : undefined;

        // Smart chunking with context
        const chunks = await this.chunker.chunkMemory(memory, previousContext);

        // Generate embeddings for chunks
        const chunksWithEmbeddings = await Promise.all(
            chunks.map(async (chunk) => {
                const embedding = await this.embeddings.embed(chunk.contextualContent);
                return {
                    ...chunk,
                    id: crypto.randomUUID(),
                    embedding
                };
            })
        );

        // Save chunks to PostgreSQL and Qdrant in parallel
        await Promise.all([
            this.postgres.saveChunks(chunksWithEmbeddings),
            this.qdrant.upsertChunks(chunksWithEmbeddings)
        ]);

        return memory;
    }

    async searchMemory(options: SearchOptions): Promise<SearchResult[]> {
        // Check hot memory first for recent conversations
        if (options.platform) {
            const hotMemory = await this.redis.getHotMemory(options.userId, options.platform);
            if (hotMemory.length > 0) {
                // Quick relevance check on hot memory
                const relevant = this.quickRelevanceFilter(options.query, hotMemory);
                if (relevant.length > 0) {
                    // Combine with deep search
                    const deepResults = await this.search.search(options);
                    return this.deduplicateResults([...this.convertToSearchResults(relevant), ...deepResults]);
                }
            }
        }

        // Full hybrid search
        return await this.search.search(options);
    }

    private quickRelevanceFilter(query: string, memories: MemoryEntry[]): MemoryEntry[] {
        const queryLower = query.toLowerCase();
        const keywords = queryLower.split(/\s+/).filter(w => w.length > 3);

        return memories.filter(memory => {
            const contentLower = memory.content.toLowerCase();
            return keywords.some(keyword => contentLower.includes(keyword));
        });
    }

    private convertToSearchResults(memories: MemoryEntry[]): SearchResult[] {
        return memories.map(memory => ({
            chunk: {
                id: memory.id,
                memoryId: memory.id,
                content: memory.content,
                contextualContent: memory.content,
                position: 0,
                metadata: memory.metadata
            },
            score: 1.0,
            relevance: 1.0,
            memory
        }));
    }

    private deduplicateResults(results: SearchResult[]): SearchResult[] {
        const seen = new Set<string>();
        return results.filter(result => {
            if (seen.has(result.chunk.id)) {
                return false;
            }
            seen.add(result.chunk.id);
            return true;
        });
    }

    async close(): Promise<void> {
        await Promise.all([
            this.postgres.close(),
            this.redis.close()
        ]);
    }
}
