-- ========================================
-- WorkTracker 데이터베이스 초기화
-- ========================================

-- 기존 테이블 및 정책 삭제 (있다면)
-- 테이블을 먼저 삭제하면 CASCADE로 관련 정책도 함께 삭제됨
DROP TABLE IF EXISTS work_logs CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- 기존 함수 및 트리거 삭제
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_work_logs_updated_at ON work_logs;
DROP FUNCTION IF EXISTS update_updated_at_column();

-- 기존 뷰 삭제
DROP VIEW IF EXISTS user_summary;

-- departments 테이블 생성
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- users 테이블 생성
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    department_id INTEGER REFERENCES departments(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- work_logs 테이블 생성
CREATE TABLE work_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    department_id INTEGER REFERENCES departments(id),
    work_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    work_hours DECIMAL(4,2),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 기본 데이터 삽입
INSERT INTO departments (name) VALUES 
    ('B동보충'),
    ('A지상보충'),
    ('A지하보충');

-- 관리자 계정 생성 (비밀번호: 0000)
INSERT INTO users (username, password_hash, role) VALUES 
    ('admin', '0000', 'admin');

-- 인덱스 생성
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_department ON users(department_id);
CREATE INDEX idx_work_logs_user_date ON work_logs(user_id, work_date);
CREATE INDEX idx_work_logs_department ON work_logs(department_id);

-- RLS (Row Level Security) 활성화
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;

-- RLS 정책 생성 (세션 기반 인증용)
-- departments: 모든 사용자가 읽기 가능
CREATE POLICY "departments_read_policy" ON departments
    FOR SELECT USING (true);

-- users: 회원가입 허용, 관리자는 모든 사용자 관리 가능
CREATE POLICY "users_insert_policy" ON users
    FOR INSERT WITH CHECK (true);

CREATE POLICY "users_read_policy" ON users
    FOR SELECT USING (true);

CREATE POLICY "users_update_policy" ON users
    FOR UPDATE USING (true);

-- work_logs: 모든 사용자가 읽기/쓰기 가능 (애플리케이션 레벨에서 권한 제어)
CREATE POLICY "work_logs_read_policy" ON work_logs
    FOR SELECT USING (true);

CREATE POLICY "work_logs_insert_policy" ON work_logs
    FOR INSERT WITH CHECK (true);

CREATE POLICY "work_logs_update_policy" ON work_logs
    FOR UPDATE USING (true);

CREATE POLICY "work_logs_delete_policy" ON work_logs
    FOR DELETE USING (true);

-- 함수 생성: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_logs_updated_at BEFORE UPDATE ON work_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 확인용 뷰 생성
CREATE VIEW user_summary AS
SELECT 
    u.id,
    u.username,
    u.role,
    d.name as department_name,
    COUNT(wl.id) as total_logs,
    SUM(wl.work_hours) as total_hours
FROM users u
LEFT JOIN departments d ON u.department_id = d.id
LEFT JOIN work_logs wl ON u.id = wl.user_id
GROUP BY u.id, u.username, u.role, d.name;

-- 완료 메시지
SELECT '데이터베이스 초기화 완료!' as status; 