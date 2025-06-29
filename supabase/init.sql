-- departments 테이블 생성 (소속 관리)
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT now()
);

-- 기본 소속 데이터 삽입
INSERT INTO departments (name) VALUES 
    ('B동입고'),
    ('A지상보충'),
    ('A지하보충');

-- users 테이블 생성 (소속 필드 추가)
CREATE TABLE users (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    username TEXT NOT NULL,
    role TEXT DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    department_id INTEGER REFERENCES departments(id),
    created_at TIMESTAMP DEFAULT now()
);

-- tasks 테이블 생성
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    task_type TEXT NOT NULL CHECK (task_type IN ('인출', '보충', '입고지원', '미출대응', '단내리기', '이고', '과출', '파손', '기타')),
    description TEXT,
    status TEXT DEFAULT '진행중' CHECK (status IN ('진행중', '완료')),
    assigned_to UUID REFERENCES users(id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT now()
);

-- logs 테이블 생성
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT now()
);

-- RLS 활성화
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

-- departments RLS 정책 (모든 사용자가 조회 가능)
CREATE POLICY "모든 사용자 소속 조회" ON departments FOR SELECT USING (true);

-- 관리자만 소속 관리 가능
CREATE POLICY "관리자 소속 관리" ON departments FOR ALL USING (
    EXISTS (
        SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'
    )
);

-- RLS 정책 설정
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

-- 사용자 정책
CREATE POLICY "본인 정보 조회" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "본인 정보 수정" ON users FOR UPDATE USING (auth.uid() = id);

-- 관리자 정책 (모든 사용자 정보 접근 가능)
CREATE POLICY "관리자 모든 사용자 접근" ON users FOR ALL USING (
    EXISTS (
        SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'
    )
);

-- 로그 정책
CREATE POLICY "로그 조회" ON logs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "로그 생성" ON logs FOR INSERT WITH CHECK (auth.uid() = user_id); 