# WorkTracker

Flask + Supabase 기반 업무 기록 웹앱

## 주요 기능
- 사용자 인증 (Supabase Auth)
- 업무 CRUD 및 Excel 출력
- 관리자 대시보드
- 역할 기반 권한 관리

## 실행 방법
1. `pip install -r requirements.txt` 설치
2. `env.example`를 `.env`로 복사하고 설정
3. `python app.py` 실행

## 배포
- CloudType, GitHub Actions 등 지원

## 기술 스택
- Frontend: HTML, CSS, JavaScript (Vanilla)
- Backend: Python (Flask)
- Database: Supabase (PostgreSQL)
- Auth: Supabase Auth 