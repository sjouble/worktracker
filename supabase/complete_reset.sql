-- ========================================
-- WorkTracker 완전 통합 초기화 SQL (KST 시간대 적용)
-- 모든 객체를 안전하게 삭제 후 새로 생성
-- ========================================

-- ========================================
-- 1단계: 모든 객체 완전 삭제 (의존성 순서 고려)
-- ========================================

-- 뷰 삭제 (테이블에 의존)
DROP VIEW IF EXISTS user_summary CASCADE;

-- 트리거 삭제 (함수에 의존)
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_work_logs_updated_at ON work_logs;

-- 함수 삭제
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- 테이블 삭제 (CASCADE로 관련 정책도 함께 삭제)
DROP TABLE IF EXISTS work_logs CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- ========================================
-- 2단계: 테이블 생성 (기본 구조)
-- ========================================

-- departments 테이블 생성
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul')
);

-- users 테이블 생성
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    department_id INTEGER REFERENCES departments(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul'),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul')
);

-- work_logs 테이블 생성
CREATE TABLE work_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    department_id INTEGER REFERENCES departments(id),
    work_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    task_type VARCHAR(50) NOT NULL,
    description TEXT,
    complete_description TEXT,
    status VARCHAR(20) DEFAULT '진행중' CHECK (status IN ('진행중', '완료')),
    work_hours DECIMAL(4,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul'),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul')
);

-- ========================================
-- 3단계: 함수 및 트리거 생성
-- ========================================

-- updated_at 자동 업데이트 함수 (KST)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul');
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_logs_updated_at 
    BEFORE UPDATE ON work_logs
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 4단계: 기본 데이터 삽입
-- ========================================

-- 기본 소속 데이터
INSERT INTO departments (name) VALUES 
    ('B동보충'),
    ('A지상보충'),
    ('A지하보충');

-- 관리자 계정 생성 (비밀번호: 0000)
INSERT INTO users (username, password_hash, role) VALUES 
    ('admin', '0000', 'admin');

-- ========================================
-- 5단계: 인덱스 생성
-- ========================================

-- 사용자 인덱스
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_department ON users(department_id);

-- 업무 로그 인덱스
CREATE INDEX idx_work_logs_user_date ON work_logs(user_id, work_date);
CREATE INDEX idx_work_logs_department ON work_logs(department_id);
CREATE INDEX idx_work_logs_status ON work_logs(status);
CREATE INDEX idx_work_logs_task_type ON work_logs(task_type);

-- ========================================
-- 6단계: RLS (Row Level Security) 설정
-- ========================================

-- RLS 활성화
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;

-- departments 정책
CREATE POLICY "departments_read_policy" ON departments
    FOR SELECT USING (true);

-- users 정책
CREATE POLICY "users_insert_policy" ON users
    FOR INSERT WITH CHECK (true);
CREATE POLICY "users_read_policy" ON users
    FOR SELECT USING (true);
CREATE POLICY "users_update_policy" ON users
    FOR UPDATE USING (true);

-- work_logs 정책
CREATE POLICY "work_logs_read_policy" ON work_logs
    FOR SELECT USING (true);
CREATE POLICY "work_logs_insert_policy" ON work_logs
    FOR INSERT WITH CHECK (true);
CREATE POLICY "work_logs_update_policy" ON work_logs
    FOR UPDATE USING (true);
CREATE POLICY "work_logs_delete_policy" ON work_logs
    FOR DELETE USING (true);

-- ========================================
-- 7단계: 뷰 생성
-- ========================================

-- 사용자 요약 뷰
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

-- ========================================
-- 8단계: 확인 및 완료
-- ========================================

-- 현재 시간 확인 (KST)
SELECT 
    NOW() as current_utc_time,
    (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul') as current_kst_time;

-- 생성된 테이블 확인
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;

-- 생성된 함수 확인
SELECT 
    proname as function_name,
    prosrc as function_source
FROM pg_proc 
WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
AND proname = 'update_updated_at_column';

-- 생성된 트리거 확인
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table
FROM information_schema.triggers 
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

-- 완료 메시지
SELECT '🎉 WorkTracker 데이터베이스 완전 초기화(KST) 성공!' as status; 