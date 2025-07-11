# WorkTracker - 업무 관리 시스템

WorkTracker는 사용자별 업무를 추적하고 관리하는 웹 애플리케이션입니다.

## 주요 기능

### 사용자 관리
- 사용자 회원가입 및 로그인
- **소속 관리**: B동보충, A지상보충, A지하보충 등 소속별 사용자 관리
- 관리자 계정으로 전체 사용자 관리

### 업무 관리
- **업무 시작**: 오늘 날짜 기본, 시작 시간만 입력, 24시간 표기법
- **업무 유형**: 인출, 보충, 입고지원, 미출대응, 단내리기, 이고, 과출, 파손, 기타
- **진행 상태**: 진행중/완료 상태 실시간 표시
- **업무 완료**: 종료 시간 입력 시 완료 처리, 완료 내용 기록
- **시간 관리**: 소요 시간 자동 계산 (24시간 형식)
- **조회 기능**: 오늘/특정 날짜/기간별 업무 조회
- **시간대**: 한국 시간대(KST) 기준으로 모든 시간 처리

### 관리자 기능
- **소속 관리**: 새 소속 추가, 수정, 삭제
- **사용자 소속 변경**: 관리자가 사용자의 소속을 변경 가능
- **전체 사용자 업무 현황 조회**: 필터링 및 검색 기능
- **실시간 통계**: 오늘 작업 참여자 수, 진행중인 업무 수, 총 업무 수
- **업무 관리**: 모든 사용자의 업무 수정/삭제 가능

## 기술 스택

- **Backend**: Flask (Python)
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Authentication**: Session-based
- **Deployment**: Render
- **Timezone**: 한국 시간대(KST) 지원

## 배포 방법 (Render)

### 1. Supabase 설정

1. [Supabase](https://supabase.com)에서 새 프로젝트 생성
2. SQL 편집기에서 `supabase/reset_database.sql` 실행 (완전 초기화)
3. **시간대 수정**: `supabase/fix_timezone.sql` 실행 (기존 데이터가 있는 경우)

### 2. Render 배포

1. [Render](https://render.com)에서 새 Web Service 생성
2. GitHub 저장소 연결
3. 환경 변수 설정:
   - `SUPABASE_URL`: Supabase 프로젝트 URL
   - `SUPABASE_KEY`: Supabase anon key
   - `FLASK_SECRET_KEY`: Flask 시크릿 키 (자동 생성됨)

### 3. 자동 배포

- `render.yaml` 파일이 포함되어 있어 자동으로 설정됩니다
- GitHub에 푸시하면 자동으로 배포됩니다

## 로컬 개발

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 Supabase 설정을 추가하세요:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
FLASK_SECRET_KEY=your_secret_key
```

### 3. 애플리케이션 실행

```bash
python app.py
```

브라우저에서 `http://localhost:5000`으로 접속하세요.

## 사용법

### 관리자 계정
- **사용자명**: admin
- **비밀번호**: 0000

### 일반 사용자
1. 회원가입 시 소속 선택 필수
2. **업무 시작**: 날짜(오늘 기본), 시작 시간(현재 시간 기본), 업무 유형, 업무 내용 입력
3. **업무 완료**: 진행중인 업무의 "완료" 버튼 클릭 → 종료 시간, 완료 내용 입력
4. **업무 조회**: 오늘/특정 날짜/기간별 조회 가능
5. **진행 상태**: 진행중인 업무는 "진행중" 배지로 표시
6. **업무 수정**: 진행중인 업무는 수정 가능

### 소속 관리 (관리자 전용)
1. 관리자 대시보드에서 "소속 관리" 섹션 확인
2. "새 소속 추가" 버튼으로 소속 생성
3. 기존 소속 수정/삭제 가능
4. 사용자별 소속 변경 기능

## 데이터베이스 구조

### departments (소속)
- `id`: 소속 ID (Primary Key)
- `name`: 소속명 (Unique)
- `created_at`: 생성일시 (KST)

### users (사용자)
- `id`: 사용자 ID (UUID, Primary Key)
- `username`: 사용자명 (Unique)
- `role`: 역할 (admin/user)
- `department_id`: 소속 ID (Foreign Key)
- `created_at`: 가입일시 (KST)
- `updated_at`: 수정일시 (KST)

### work_logs (업무 로그)
- `id`: 로그 ID (Primary Key)
- `user_id`: 사용자 ID (Foreign Key)
- `department_id`: 소속 ID (Foreign Key)
- `work_date`: 업무 날짜
- `start_time`: 시작 시간 (TIME)
- `end_time`: 종료 시간 (TIME)
- `task_type`: 업무 유형 (VARCHAR)
- `description`: 업무 내용 (TEXT)
- `complete_description`: 완료 내용 (TEXT)
- `status`: 상태 (진행중/완료)
- `work_hours`: 소요 시간 (DECIMAL)
- `created_at`: 생성일시 (KST)
- `updated_at`: 수정일시 (KST)

## 최근 업데이트

### v2.0 (2024년)
- **시간대 수정**: 모든 시간을 한국 시간대(KST) 기준으로 처리
- **관리자 대시보드 개선**: 실시간 통계 및 업무 관리 기능 강화
- **UI/UX 개선**: 모달 다이얼로그, 토스트 메시지, 반응형 디자인
- **권한 관리 강화**: 관리자 권한으로 모든 업무 관리 가능
- **버그 수정**: 업무 수정/삭제 기능 개선

## 문제 해결

### 시간대 문제
- 모든 시간은 한국 시간대(KST) 기준으로 저장됩니다
- 기존 데이터가 있다면 `supabase/fix_timezone.sql` 실행
- 프론트엔드에서도 한국 시간대로 표시됩니다

### 배포 문제
- Render에서 환경 변수가 올바르게 설정되었는지 확인
- Supabase 프로젝트 URL과 API 키가 정확한지 확인
- 로그를 확인하여 구체적인 오류 메시지 확인

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 