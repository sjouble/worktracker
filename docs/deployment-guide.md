# WorkTracker Render 배포 가이드

이 문서는 WorkTracker 애플리케이션을 Render에서 배포하는 방법을 설명합니다.

## 사전 준비

### 1. Supabase 프로젝트 설정

1. [Supabase](https://supabase.com)에 가입하고 새 프로젝트 생성
2. 프로젝트 생성 후 Settings > API에서 다음 정보 확인:
   - Project URL
   - anon public key

### 2. 데이터베이스 초기화

1. Supabase 대시보드에서 SQL Editor 열기
2. `supabase/init_database.sql` 파일의 내용을 복사하여 실행
3. `supabase/rls_policies.sql` 파일의 내용도 실행

## Render 배포

### 1. GitHub 저장소 준비

1. 프로젝트를 GitHub 저장소에 푸시
2. 저장소가 공개되어 있는지 확인

### 2. Render 서비스 생성

1. [Render](https://render.com)에 가입/로그인
2. "New +" 버튼 클릭 후 "Web Service" 선택
3. GitHub 저장소 연결
4. 저장소 선택 후 다음 설정 적용:

#### 기본 설정
- **Name**: worktracker (또는 원하는 이름)
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn wsgi:app`

#### 환경 변수 설정
- **SUPABASE_URL**: Supabase 프로젝트 URL
- **SUPABASE_KEY**: Supabase anon public key
- **FLASK_SECRET_KEY**: 랜덤 문자열 (자동 생성됨)

### 3. 자동 배포 설정

- **Auto-Deploy**: Yes (기본값)
- **Branch**: main (또는 사용하는 브랜치)

### 4. 배포 완료

배포가 완료되면 Render에서 제공하는 URL로 접속 가능합니다.

## 환경 변수 관리

### 로컬 개발용 (.env 파일)

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
FLASK_SECRET_KEY=your-secret-key
```

### Render 환경 변수

Render 대시보드에서 Environment Variables 섹션에서 설정:

| 변수명 | 설명 | 예시 |
|--------|------|------|
| SUPABASE_URL | Supabase 프로젝트 URL | https://abc123.supabase.co |
| SUPABASE_KEY | Supabase anon key | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| FLASK_SECRET_KEY | Flask 시크릿 키 | 자동 생성됨 |

## 문제 해결

### 일반적인 문제들

1. **Supabase 연결 실패**
   - 환경 변수가 올바르게 설정되었는지 확인
   - Supabase 프로젝트가 활성 상태인지 확인

2. **빌드 실패**
   - requirements.txt 파일이 올바른지 확인
   - Python 버전 호환성 확인

3. **애플리케이션 시작 실패**
   - 로그 확인 (Render 대시보드 > Logs)
   - wsgi.py 파일이 올바른지 확인

### 로그 확인

Render 대시보드에서:
1. 서비스 선택
2. "Logs" 탭 클릭
3. 실시간 로그 확인

## 보안 고려사항

1. **환경 변수 보호**
   - 민감한 정보는 환경 변수로 관리
   - .env 파일을 .gitignore에 포함

2. **Supabase RLS 정책**
   - 데이터베이스 레벨 보안 정책 적용
   - 사용자별 데이터 접근 제한

3. **HTTPS 사용**
   - Render는 자동으로 HTTPS 제공
   - 프로덕션에서는 항상 HTTPS 사용

## 모니터링

### Render 대시보드에서 확인 가능한 정보

- 서비스 상태 (Healthy/Unhealthy)
- 응답 시간
- 에러율
- 리소스 사용량

### 알림 설정

- 서비스 다운 시 이메일 알림
- 에러율 임계값 설정

## 업데이트 및 유지보수

### 코드 업데이트

1. 로컬에서 코드 수정
2. GitHub에 푸시
3. Render에서 자동 배포

### 데이터베이스 마이그레이션

1. Supabase SQL Editor에서 스크립트 실행
2. 애플리케이션 재시작 (필요시)

### 백업

- Supabase는 자동 백업 제공
- 정기적인 데이터베이스 백업 권장 