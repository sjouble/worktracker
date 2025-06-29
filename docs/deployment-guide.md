# WorkTracker 배포 가이드

## 1. Supabase 설정

### 1.1 Supabase 프로젝트 생성
1. [Supabase](https://supabase.com)에 로그인
2. 새 프로젝트 생성
3. 프로젝트 URL과 API 키 확인

### 1.2 데이터베이스 초기화
1. Supabase Dashboard → SQL Editor
2. `supabase/init.sql` 파일의 내용을 실행
3. 테이블과 RLS 정책이 생성되었는지 확인

### 1.3 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 입력:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
FLASK_SECRET_KEY=your_random_secret_key
```

## 2. 로컬 개발 환경

### 2.1 의존성 설치
```bash
pip install -r requirements.txt
```

### 2.2 애플리케이션 실행
```bash
python app.py
```

### 2.3 접속
브라우저에서 `http://localhost:5000` 접속

## 3. CloudType 배포

### 3.1 GitHub 저장소 연결
1. GitHub에 코드 푸시
2. CloudType에서 GitHub 저장소 연결

### 3.2 환경 변수 설정
CloudType 대시보드에서 환경 변수 설정:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `FLASK_SECRET_KEY`

### 3.3 배포 설정
- **빌드 명령어**: `pip install -r requirements.txt`
- **실행 명령어**: `gunicorn --bind 0.0.0.0:5000 app:app`
- **포트**: 5000

## 4. 관리자 계정 생성

### 4.1 첫 번째 사용자 등록
1. 일반 사용자로 회원가입
2. Supabase Dashboard → Table Editor → users
3. 해당 사용자의 role을 'admin'으로 변경

### 4.2 SQL로 관리자 생성
```sql
UPDATE users 
SET role = 'admin' 
WHERE email = 'admin@example.com';
```

## 5. 보안 고려사항

### 5.1 환경 변수
- `.env` 파일을 `.gitignore`에 추가
- 프로덕션에서는 환경 변수 사용

### 5.2 RLS 정책
- Supabase RLS가 활성화되어 있는지 확인
- 사용자별 데이터 접근 제한 확인

### 5.3 HTTPS
- 프로덕션 환경에서는 HTTPS 사용 필수

## 6. 모니터링 및 로그

### 6.1 로그 확인
- Supabase Dashboard → Logs
- 애플리케이션 로그 확인

### 6.2 성능 모니터링
- Supabase Dashboard → Analytics
- 데이터베이스 성능 확인

## 7. 백업 및 복구

### 7.1 데이터 백업
- Supabase Dashboard → Settings → Database
- 정기적인 백업 설정

### 7.2 코드 백업
- GitHub 저장소 활용
- 정기적인 커밋 및 푸시

## 8. 문제 해결

### 8.1 일반적인 문제
- **연결 오류**: 환경 변수 확인
- **권한 오류**: RLS 정책 확인
- **파일 업로드 오류**: exports 폴더 권한 확인

### 8.2 로그 확인
- Flask 애플리케이션 로그
- Supabase 로그
- 브라우저 개발자 도구 콘솔 