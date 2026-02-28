-- BookLeaf AI Assistant Database Schema
-- PostgreSQL 15+ with pgvector extension

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Drop tables if they exist (for development)
DROP TABLE IF EXISTS query_analytics CASCADE;
DROP TABLE IF EXISTS escalations CASCADE;
DROP TABLE IF EXISTS knowledge_embeddings CASCADE;
DROP TABLE IF EXISTS knowledge_documents CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS identities CASCADE;
DROP TABLE IF EXISTS authors CASCADE;

-- Authors table: Core author information
CREATE TABLE authors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_authors_email ON authors(email);
CREATE INDEX idx_authors_phone ON authors(phone);
CREATE INDEX idx_authors_full_name ON authors(full_name);

-- Identities table: Platform-specific identities linked to authors
CREATE TABLE identities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    author_id UUID REFERENCES authors(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- 'email', 'whatsapp', 'instagram', 'web_chat'
    platform_identifier VARCHAR(255) NOT NULL, -- email address, phone, username, session_id
    normalized_identifier VARCHAR(255), -- normalized version for matching
    confidence_score FLOAT DEFAULT 1.0, -- 0.0 to 1.0
    matching_method VARCHAR(50), -- 'exact', 'fuzzy', 'llm', 'manual'
    matching_metadata JSONB DEFAULT '{}',
    verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(platform, platform_identifier)
);

CREATE INDEX idx_identities_author ON identities(author_id);
CREATE INDEX idx_identities_platform ON identities(platform, platform_identifier);
CREATE INDEX idx_identities_normalized ON identities(normalized_identifier);

-- Conversations table: Chat conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    author_id UUID REFERENCES authors(id) ON DELETE SET NULL,
    identity_id UUID REFERENCES identities(id) ON DELETE SET NULL,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'closed', 'escalated'
    metadata JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_conversations_author ON conversations(author_id);
CREATE INDEX idx_conversations_identity ON conversations(identity_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_platform ON conversations(platform);

-- Messages table: Individual messages in conversations
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    intent VARCHAR(100), -- 'author_specific', 'general_knowledge', 'technical_support', 'out_of_scope'
    confidence_score FLOAT, -- Overall confidence score for this message
    confidence_breakdown JSONB, -- Detailed confidence calculation
    rag_context JSONB, -- Retrieved RAG context used for response
    llm_model VARCHAR(100), -- Model used for generation
    processing_time_ms INTEGER, -- Time to process and generate response
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_intent ON messages(intent);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

-- Knowledge documents table: Source documents for RAG
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    document_type VARCHAR(100), -- 'publishing_process', 'royalty_structure', etc.
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_knowledge_documents_type ON knowledge_documents(document_type);

-- Knowledge embeddings table: Vector embeddings for RAG retrieval
CREATE TABLE knowledge_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(1536), -- OpenAI text-embedding-3-large dimensions
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_knowledge_embeddings_document ON knowledge_embeddings(document_id);
CREATE INDEX idx_knowledge_embeddings_vector ON knowledge_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Escalations table: Queries escalated to human agents
CREATE TABLE escalations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    reason VARCHAR(500) NOT NULL,
    priority VARCHAR(50) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'in_progress', 'resolved', 'cancelled'
    assigned_to VARCHAR(255),
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_escalations_conversation ON escalations(conversation_id);
CREATE INDEX idx_escalations_status ON escalations(status);
CREATE INDEX idx_escalations_priority ON escalations(priority);
CREATE INDEX idx_escalations_created_at ON escalations(created_at DESC);

-- Query analytics table: Performance and usage metrics
CREATE TABLE query_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    intent VARCHAR(100),
    confidence_score FLOAT,
    escalated BOOLEAN DEFAULT false,
    response_time_ms INTEGER,
    llm_model VARCHAR(100),
    llm_tokens_input INTEGER,
    llm_tokens_output INTEGER,
    rag_retrieved_chunks INTEGER,
    identity_match_method VARCHAR(50),
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_query_analytics_intent ON query_analytics(intent);
CREATE INDEX idx_query_analytics_escalated ON query_analytics(escalated);
CREATE INDEX idx_query_analytics_created_at ON query_analytics(created_at DESC);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_authors_updated_at BEFORE UPDATE ON authors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_identities_updated_at BEFORE UPDATE ON identities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_documents_updated_at BEFORE UPDATE ON knowledge_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update conversation last_message_at
CREATE OR REPLACE FUNCTION update_conversation_last_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET last_message_at = NEW.created_at
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_conversation_last_message_trigger AFTER INSERT ON messages
    FOR EACH ROW EXECUTE FUNCTION update_conversation_last_message();

-- Comments for documentation
COMMENT ON TABLE authors IS 'Core author information';
COMMENT ON TABLE identities IS 'Platform-specific identities linked to authors with confidence scoring';
COMMENT ON TABLE conversations IS 'Chat conversations across multiple platforms';
COMMENT ON TABLE messages IS 'Individual messages with intent classification and confidence scoring';
COMMENT ON TABLE knowledge_documents IS 'Source documents for RAG system';
COMMENT ON TABLE knowledge_embeddings IS 'Vector embeddings for semantic search using pgvector';
COMMENT ON TABLE escalations IS 'Queries escalated to human agents for manual handling';
COMMENT ON TABLE query_analytics IS 'Performance and usage metrics for monitoring and optimization';

-- Grant permissions (adjust based on your Supabase setup)
-- Note: Supabase typically handles permissions through RLS policies
-- These are basic grants for service role access
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO postgres;
