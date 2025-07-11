-- ========================================
-- WorkTracker 데이터베이스 마이그레이션
-- 기존 테이블에 새로운 컬럼 추가
-- ========================================

-- work_logs 테이블에 새로운 컬럼들 추가
ALTER TABLE work_logs 
ADD COLUMN IF NOT EXISTS task_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS complete_description TEXT,
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT '진행중' CHECK (status IN ('진행중', '완료'));

-- 기존 레코드들의 status를 '완료'로 설정 (end_time이 있는 경우)
UPDATE work_logs 
SET status = '완료' 
WHERE end_time IS NOT NULL AND status IS NULL;

-- 기존 레코드들의 status를 '진행중'으로 설정 (end_time이 없는 경우)
UPDATE work_logs 
SET status = '진행중' 
WHERE end_time IS NULL AND status IS NULL;

-- task_type이 NULL인 기존 레코드들을 '기타'로 설정
UPDATE work_logs 
SET task_type = '기타' 
WHERE task_type IS NULL;

-- id 컬럼을 UUID로 변경 (기존 SERIAL에서)
-- 먼저 기존 인덱스와 제약조건 제거
DROP INDEX IF EXISTS idx_work_logs_user_date;
DROP INDEX IF EXISTS idx_work_logs_department;

-- 새로운 UUID 컬럼 추가
ALTER TABLE work_logs 
ADD COLUMN IF NOT EXISTS new_id UUID DEFAULT gen_random_uuid();

-- 기존 데이터에 UUID 생성
UPDATE work_logs 
SET new_id = gen_random_uuid() 
WHERE new_id IS NULL;

-- 기존 id 컬럼 삭제하고 new_id를 id로 이름 변경
ALTER TABLE work_logs DROP COLUMN IF EXISTS id;
ALTER TABLE work_logs RENAME COLUMN new_id TO id;
ALTER TABLE work_logs ALTER COLUMN id SET NOT NULL;

-- Primary Key 제약조건 추가
ALTER TABLE work_logs ADD PRIMARY KEY (id);

-- 인덱스 재생성
CREATE INDEX IF NOT EXISTS idx_work_logs_user_date ON work_logs(user_id, work_date);
CREATE INDEX IF NOT EXISTS idx_work_logs_department ON work_logs(department_id);
CREATE INDEX IF NOT EXISTS idx_work_logs_status ON work_logs(status);
CREATE INDEX IF NOT EXISTS idx_work_logs_task_type ON work_logs(task_type);

-- 완료 메시지
SELECT '데이터베이스 마이그레이션 완료!' as status; 