-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Memory entries table
CREATE TABLE IF NOT EXISTS memory_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    conversation_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Chunks table with embeddings
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID NOT NULL REFERENCES memory_entries(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    contextual_content TEXT NOT NULL,
    embedding vector(1024), -- Voyage AI / Cohere dimension
    position INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_memory_user_id ON memory_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_platform ON memory_entries(platform);
CREATE INDEX IF NOT EXISTS idx_memory_conversation ON memory_entries(conversation_id);
CREATE INDEX IF NOT EXISTS idx_memory_timestamp ON memory_entries(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_memory_user_timestamp ON memory_entries(user_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_chunks_memory_id ON chunks(memory_id);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Full text search
CREATE INDEX IF NOT EXISTS idx_memory_content_fts ON memory_entries USING gin(to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_chunks_content_fts ON chunks USING gin(to_tsvector('english', content));

-- Conversation summary table for efficient context retrieval
CREATE TABLE IF NOT EXISTS conversation_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    conversation_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    summary TEXT NOT NULL,
    message_count INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, conversation_id, platform)
);

CREATE INDEX IF NOT EXISTS idx_conv_summary_user ON conversation_summaries(user_id);
