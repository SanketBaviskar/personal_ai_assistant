-- Add metadata column to document_embeddings table
ALTER TABLE document_embeddings
ADD COLUMN metadata JSONB DEFAULT '{}'::jsonb;

-- Create index for faster metadata querying (optional but good for future)
CREATE INDEX idx_document_embeddings_metadata ON document_embeddings USING gin (metadata);
