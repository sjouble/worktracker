-- ========================================
-- WorkTracker 시간대 수정 SQL
-- 기존 데이터베이스의 시간대를 한국 시간대로 수정
-- ========================================

-- 1. 기존 함수 삭제 후 재생성 (한국 시간대 기준)
DROP FUNCTION IF EXISTS update_updated_at_column();

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul');
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 2. 기존 트리거 삭제 후 재생성
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_work_logs_updated_at ON work_logs;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_logs_updated_at BEFORE UPDATE ON work_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 3. 기존 데이터의 시간대 수정 (UTC → KST)
-- departments 테이블의 created_at 수정
UPDATE departments 
SET created_at = (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul')
WHERE created_at IS NOT NULL;

-- users 테이블의 created_at, updated_at 수정
UPDATE users 
SET 
    created_at = (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul'),
    updated_at = (updated_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul')
WHERE created_at IS NOT NULL OR updated_at IS NOT NULL;

-- work_logs 테이블의 created_at, updated_at 수정
UPDATE work_logs 
SET 
    created_at = (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul'),
    updated_at = (updated_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul')
WHERE created_at IS NOT NULL OR updated_at IS NOT NULL;

-- 4. 컬럼 기본값 수정 (새로 생성되는 레코드용)
-- departments 테이블
ALTER TABLE departments 
ALTER COLUMN created_at SET DEFAULT (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul');

-- users 테이블
ALTER TABLE users 
ALTER COLUMN created_at SET DEFAULT (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul'),
ALTER COLUMN updated_at SET DEFAULT (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul');

-- work_logs 테이블
ALTER TABLE work_logs 
ALTER COLUMN created_at SET DEFAULT (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul'),
ALTER COLUMN updated_at SET DEFAULT (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul');

-- 5. 확인용 쿼리
SELECT '시간대 수정 완료!' as status;

-- 현재 시간 확인 (한국 시간대)
SELECT 
    NOW() as current_utc_time,
    (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul') as current_kst_time;

-- 최근 업무 로그 시간 확인
SELECT 
    id,
    created_at,
    updated_at,
    work_date,
    start_time
FROM work_logs 
ORDER BY created_at DESC 
LIMIT 5; 