-- Row Level Security (RLS) 정책 설정

-- tasks 테이블 RLS 정책
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- 일반 사용자 정책
CREATE POLICY "본인 업무 조회" ON tasks FOR SELECT USING (auth.uid() = assigned_to);
CREATE POLICY "본인 업무 수정" ON tasks FOR UPDATE USING (auth.uid() = assigned_to);
CREATE POLICY "본인 업무 삭제" ON tasks FOR DELETE USING (auth.uid() = assigned_to);
CREATE POLICY "업무 등록 허용" ON tasks FOR INSERT WITH CHECK (auth.uid() = assigned_to);

-- 관리자 정책 (모든 업무 접근 가능)
CREATE POLICY "관리자 모든 업무 접근" ON tasks FOR ALL USING (
    EXISTS (
        SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'
    )
);

-- users 테이블 RLS 정책
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "본인 정보 조회" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "본인 정보 수정" ON users FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "사용자 생성" ON users FOR INSERT WITH CHECK (auth.uid() = id);

-- 관리자 정책 (모든 사용자 정보 접근 가능)
CREATE POLICY "관리자 모든 사용자 접근" ON users FOR ALL USING (
    EXISTS (
        SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'
    )
);

-- logs 테이블 RLS 정책
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "본인 로그 조회" ON logs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "로그 생성" ON logs FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 관리자 정책 (모든 로그 접근 가능)
CREATE POLICY "관리자 모든 로그 접근" ON logs FOR ALL USING (
    EXISTS (
        SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'
    )
); 