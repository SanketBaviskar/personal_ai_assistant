-- Resize embedding column to 384 dimensions for all-MiniLM-L6-v2
ALTER TABLE document_embeddings 
ALTER COLUMN embedding TYPE vector(384);

-- Recreate the index with the new dimension match
DROP INDEX IF EXISTS document_embeddings_embedding_idx;

CREATE INDEX document_embeddings_embedding_idx 
ON document_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
