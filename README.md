# WorkTracker - 업무 관리 시스템

WorkTracker는 사용자별 업무를 추적하고 관리하는 웹 애플리케이션입니다.

## 주요 기능

### 사용자 관리
- 사용자 회원가입 및 로그인
- **소속 관리**: B동보충, A지상보충, A지하보충 등 소속별 사용자 관리
- 관리자 계정으로 전체 사용자 관리

### 업무 관리
- 업무 유형: 인출, 보충, 입고지원, 미출대응, 단내리기, 이고, 과출, 파손, 기타
- 실시간 업무 상태 추적 (진행중/완료)
- 업무 시작/완료 시간 기록
- 소요 시간 자동 계산

### 관리자 기능
- **소속 관리**: 새 소속 추가, 수정, 삭제
- **사용자 소속 변경**: 관리자가 사용자의 소속을 변경 가능
- 전체 사용자 업무 현황 조회
- 엑셀 파일로 업무 데이터 내보내기

## 기술 스택

- **Backend**: Flask (Python)
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Authentication**: Session-based

## 설치 및 실행

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

### 3. 데이터베이스 설정

1. Supabase 프로젝트 생성
2. SQL 편집기에서 `supabase/init.sql` 실행
3. RLS 정책 설정 확인

### 4. 애플리케이션 실행

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
2. 업무 등록 및 완료 처리
3. 본인 업무 현황 조회

### 소속 관리 (관리자 전용)
1. 관리자 대시보드에서 "소속 관리" 섹션 확인
2. "새 소속 추가" 버튼으로 소속 생성
3. 기존 소속 수정/삭제 가능
4. 사용자별 소속 변경 기능

## 데이터베이스 구조

### departments (소속)
- `id`: 소속 ID (Primary Key)
- `name`: 소속명 (Unique)
- `created_at`: 생성일시

### users (사용자)
- `id`: 사용자 ID (UUID, Primary Key)
- `username`: 사용자명 (Unique)
- `role`: 역할 (admin/user)
- `department_id`: 소속 ID (Foreign Key)
- `created_at`: 가입일시

### tasks (업무)
- `id`: 업무 ID (Primary Key)
- `task_type`: 업무 유형
- `description`: 업무 설명
- `status`: 상태 (진행중/완료)
- `assigned_to`: 담당자 ID (Foreign Key)
- `start_time`: 시작 시간
- `end_time`: 종료 시간
- `created_at`: 생성일시

### logs (로그)
- `id`: 로그 ID (Primary Key)
- `user_id`: 사용자 ID (Foreign Key)
- `action`: 수행한 작업
- `timestamp`: 작업 시간

## API 엔드포인트

### 인증
- `GET /` - 메인 페이지
- `GET/POST /login` - 로그인
- `GET/POST /register` - 회원가입
- `GET /logout` - 로그아웃

### 대시보드
- `GET /dashboard` - 사용자 대시보드
- `GET /admin_dashboard` - 관리자 대시보드

### 업무 관리
- `GET /api/tasks` - 업무 목록 조회
- `POST /api/tasks` - 새 업무 생성
- `PUT /api/tasks/<id>` - 업무 수정
- `DELETE /api/tasks/<id>` - 업무 삭제
- `PUT /api/tasks/<id>/complete` - 업무 완료

### 소속 관리 (관리자 전용)
- `GET /api/departments` - 소속 목록 조회
- `POST /api/departments` - 새 소속 생성
- `PUT /api/departments/<id>` - 소속 수정
- `DELETE /api/departments/<id>` - 소속 삭제

### 사용자 관리 (관리자 전용)
- `GET /api/users` - 사용자 목록 조회
- `PUT /api/users/<id>/department` - 사용자 소속 변경

## 보안

- Row Level Security (RLS) 정책 적용
- 관리자 권한 검증
- 사용자별 데이터 접근 제한
- 세션 기반 인증

## 라이선스

MIT License 