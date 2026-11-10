
-- ExamPilot 2.0 Row Level Security (RLS) Policies for Supabase PostgreSQL
-- Enforces strict user tenant isolation across all tables

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE practice_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE practice_answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- Profiles: users can select/update only their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid()::text = id);
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid()::text = id);

-- API Providers: strict user isolation
CREATE POLICY "Users access own api_providers" ON api_providers
    FOR ALL USING (auth.uid()::text = user_id);

-- Questions: strict user isolation
CREATE POLICY "Users access own questions" ON questions
    FOR ALL USING (auth.uid()::text = user_id);

-- Subjects: strict user isolation
CREATE POLICY "Users access own subjects" ON subjects
    FOR ALL USING (auth.uid()::text = user_id);

-- Practice Sessions & Answers
CREATE POLICY "Users access own practice_sessions" ON practice_sessions
    FOR ALL USING (auth.uid()::text = user_id);
CREATE POLICY "Users access own practice_answers" ON practice_answers
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM practice_sessions
            WHERE practice_sessions.id = practice_answers.session_id
            AND practice_sessions.user_id = auth.uid()::text
        )
    );

-- Documents & Chunks
CREATE POLICY "Users access own documents" ON documents
    FOR ALL USING (auth.uid()::text = user_id);
CREATE POLICY "Users access own document_chunks" ON document_chunks
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM documents
            WHERE documents.id = document_chunks.document_id
            AND documents.user_id = auth.uid()::text
        )
    );

-- Conversations & Messages
CREATE POLICY "Users access own conversations" ON conversations
    FOR ALL USING (auth.uid()::text = user_id);
CREATE POLICY "Users access own messages" ON messages
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM conversations
            WHERE conversations.id = messages.conversation_id
            AND conversations.user_id = auth.uid()::text
        )
    );

-- Usage Logs & Settings
CREATE POLICY "Users access own usage_logs" ON usage_logs
    FOR ALL USING (auth.uid()::text = user_id);
CREATE POLICY "Users access own settings" ON user_settings
    FOR ALL USING (auth.uid()::text = user_id);
