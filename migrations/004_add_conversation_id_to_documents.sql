ALTER TABLE document ADD COLUMN conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE;
CREATE INDEX ix_document_conversation_id ON document (conversation_id);
