-- 1. Update Users Table
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_user_id UUID;
CREATE INDEX IF NOT EXISTS idx_users_auth_user_id ON users(auth_user_id);

-- 2. Update Document Table
ALTER TABLE document ADD COLUMN IF NOT EXISTS provider VARCHAR(50);
ALTER TABLE document ADD COLUMN IF NOT EXISTS external_id VARCHAR(255);
ALTER TABLE document ADD COLUMN IF NOT EXISTS source_url TEXT;
ALTER TABLE document ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64);

-- Add unique constraint for idempotency
-- We drop the constraint if it exists to be safe/idempotent in script
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_document_user_provider_external') THEN
        ALTER TABLE document ADD CONSTRAINT uq_document_user_provider_external UNIQUE (user_id, provider, external_id);
    END IF;
END $$;

-- 3. Update Document Embeddings Table
-- Warning: This clears existing embeddings to enforce data consistency with new schema
DELETE FROM document_embeddings;

ALTER TABLE document_embeddings ADD COLUMN IF NOT EXISTS document_id INTEGER REFERENCES document(id) ON DELETE CASCADE;
-- Make it NOT NULL after clearing data
ALTER TABLE document_embeddings ALTER COLUMN document_id SET NOT NULL;

-- 4. Update Messages Table (add user_id)
ALTER TABLE messages ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;

-- Backfill user_id from conversations
UPDATE messages 
SET user_id = conversations.user_id 
FROM conversations 
WHERE messages.conversation_id = conversations.id 
AND messages.user_id IS NULL;

-- Make user_id NOT NULL
ALTER TABLE messages ALTER COLUMN user_id SET NOT NULL;

-- 5. Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE document ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_credentials ENABLE ROW LEVEL SECURITY;

-- 6. RLS Policies
-- Users
DROP POLICY IF EXISTS "Users can only access their own profile" ON users;
CREATE POLICY "Users can only access their own profile" ON users
    USING (auth.uid() = auth_user_id);

-- Documents
DROP POLICY IF EXISTS "Users can only access their own documents" ON document;
CREATE POLICY "Users can only access their own documents" ON document
    USING (auth.uid() = (SELECT auth_user_id FROM users WHERE id = document.user_id));

-- Embeddings
DROP POLICY IF EXISTS "Users can only access their own embeddings" ON document_embeddings;
CREATE POLICY "Users can only access their own embeddings" ON document_embeddings
    USING (auth.uid() = (SELECT auth_user_id FROM users WHERE id = document_embeddings.user_id));

-- Conversations
DROP POLICY IF EXISTS "Users can only access their own conversations" ON conversations;
CREATE POLICY "Users can only access their own conversations" ON conversations
    USING (auth.uid() = (SELECT auth_user_id FROM users WHERE id = conversations.user_id));

-- Messages
DROP POLICY IF EXISTS "Users can only access their own messages" ON messages;
CREATE POLICY "Users can only access their own messages" ON messages
    USING (auth.uid() = (SELECT auth_user_id FROM users WHERE id = messages.user_id));

-- Credentials
DROP POLICY IF EXISTS "Users can only access their own credentials" ON user_credentials;
CREATE POLICY "Users can only access their own credentials" ON user_credentials
    USING (auth.uid() = (SELECT auth_user_id FROM users WHERE id = user_credentials.user_id));
