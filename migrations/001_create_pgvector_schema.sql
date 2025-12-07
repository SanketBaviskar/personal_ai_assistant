-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for document embeddings
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(768),  -- Assuming we'll use a 768-dimensional model (e.g., sentence-transformers)
    source_app VARCHAR(50) NOT NULL,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for fast vector similarity search
CREATE INDEX IF NOT EXISTS document_embeddings_embedding_idx 
ON document_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index for filtering by user
CREATE INDEX IF NOT EXISTS document_embeddings_user_id_idx 
ON document_embeddings(user_id);

-- Create index for filtering by source
CREATE INDEX IF NOT EXISTS document_embeddings_source_idx 
ON document_embeddings(source_app, user_id);
