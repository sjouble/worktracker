# WorkTracker API 스펙

이 문서는 WorkTracker 애플리케이션의 API 엔드포인트를 설명합니다.

## 기본 정보

- **Base URL**: `https://your-app.onrender.com`
- **Content-Type**: `application/json`
- **Authentication**: Session-based

## 인증 API

### 로그인
```
POST /login
Content-Type: application/x-www-form-urlencoded

Parameters:
- username: string (required)
- password: string (required)

Response:
- Success: Redirect to /dashboard or /admin_dashboard
- Error: HTML error page
```

### 회원가입
```
POST /register
Content-Type: application/x-www-form-urlencoded

Parameters:
- username: string (required)
- password: string (required)

Response:
{
  "success": true,
  "message": "회원가입 성공!",
  "user_id": "uuid"
}
```

### 로그아웃
```
GET /logout

Response:
- Redirect to /login
```

## 대시보드 API

### 사용자 대시보드
```
GET /dashboard

Headers:
- Cookie: session=...

Response:
- HTML dashboard page
- Redirect to /login if not authenticated
```

### 관리자 대시보드
```
GET /admin_dashboard

Headers:
- Cookie: session=...

Response:
- HTML admin dashboard page
- Redirect to /dashboard if not admin
```

## 업무 관리 API

### 업무 로그 목록 조회
```
GET /api/work_logs

Headers:
- Cookie: session=...

Query Parameters:
- user_id: string (optional, admin only)
- department_id: integer (optional)
- start_date: string (YYYY-MM-DD, optional)
- end_date: string (YYYY-MM-DD, optional)

Response:
{
  "data": [
    {
      "id": 1,
      "user_id": "uuid",
      "department_id": 1,
      "work_date": "2024-01-15",
      "start_time": "09:00:00",
      "end_time": "17:00:00",
      "work_hours": 8.0,
      "description": "업무 설명",
      "created_at": "2024-01-15T09:00:00Z",
      "users": {
        "username": "사용자명"
      }
    }
  ]
}
```

### 새 업무 로그 생성
```
POST /api/work_logs
Content-Type: application/json

Headers:
- Cookie: session=...

Body:
{
  "work_date": "2024-01-15",
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "description": "업무 설명"
}

Response:
{
  "success": true,
  "data": {
    "id": 1,
    "work_date": "2024-01-15",
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "work_hours": 8.0,
    "description": "업무 설명"
  }
}
```

### 업무 로그 수정
```
PUT /api/work_logs/{id}
Content-Type: application/json

Headers:
- Cookie: session=...

Body:
{
  "work_date": "2024-01-15",
  "start_time": "09:00:00",
  "end_time": "18:00:00",
  "description": "수정된 업무 설명"
}

Response:
{
  "success": true,
  "data": {
    "id": 1,
    "work_date": "2024-01-15",
    "start_time": "09:00:00",
    "end_time": "18:00:00",
    "work_hours": 9.0,
    "description": "수정된 업무 설명"
  }
}
```

### 업무 로그 삭제
```
DELETE /api/work_logs/{id}

Headers:
- Cookie: session=...

Response:
{
  "success": true,
  "message": "업무 로그가 삭제되었습니다."
}
```

## 소속 관리 API (관리자 전용)

### 소속 목록 조회
```
GET /api/departments

Headers:
- Cookie: session=...

Response:
{
  "data": [
    {
      "id": 1,
      "name": "B동보충",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 새 소속 생성
```
POST /api/departments
Content-Type: application/json

Headers:
- Cookie: session=...

Body:
{
  "name": "새 소속명"
}

Response:
{
  "success": true,
  "data": {
    "id": 2,
    "name": "새 소속명",
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

### 소속 수정
```
PUT /api/departments/{id}
Content-Type: application/json

Headers:
- Cookie: session=...

Body:
{
  "name": "수정된 소속명"
}

Response:
{
  "success": true,
  "data": {
    "id": 1,
    "name": "수정된 소속명",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 소속 삭제
```
DELETE /api/departments/{id}

Headers:
- Cookie: session=...

Response:
{
  "success": true,
  "message": "소속이 삭제되었습니다."
}
```

## 사용자 관리 API (관리자 전용)

### 사용자 목록 조회
```
GET /api/users

Headers:
- Cookie: session=...

Response:
{
  "data": [
    {
      "id": "uuid",
      "username": "사용자명",
      "role": "user",
      "department_id": 1,
      "created_at": "2024-01-01T00:00:00Z",
      "departments": {
        "name": "B동보충"
      }
    }
  ]
}
```

### 사용자 소속 변경
```
PUT /api/users/{id}/department
Content-Type: application/json

Headers:
- Cookie: session=...

Body:
{
  "department_id": 2
}

Response:
{
  "success": true,
  "data": {
    "id": "uuid",
    "department_id": 2,
    "departments": {
      "name": "A지상보충"
    }
  }
}
```

## 유틸리티 API

### 헬스 체크
```
GET /health

Response:
{
  "status": "healthy",
  "message": "WorkTracker is running"
}
```



## 에러 응답

### 일반적인 에러 응답
```json
{
  "error": "에러 메시지",
  "status": "error"
}
```

### HTTP 상태 코드

- `200`: 성공
- `400`: 잘못된 요청
- `401`: 인증 실패
- `403`: 권한 없음
- `404`: 리소스를 찾을 수 없음
- `500`: 서버 내부 오류

## 데이터 모델

### User
```json
{
  "id": "uuid",
  "username": "string",
  "role": "user|admin",
  "department_id": "integer",
  "created_at": "datetime"
}
```

### Department
```json
{
  "id": "integer",
  "name": "string",
  "created_at": "datetime"
}
```

### WorkLog
```json
{
  "id": "integer",
  "user_id": "uuid",
  "department_id": "integer",
  "work_date": "date",
  "start_time": "time",
  "end_time": "time",
  "work_hours": "decimal",
  "description": "text",
  "created_at": "datetime"
}
```

## 보안

### 인증
- 세션 기반 인증 사용
- 로그인 시 세션 생성
- 로그아웃 시 세션 삭제

### 권한
- 일반 사용자: 자신의 데이터만 접근 가능
- 관리자: 모든 데이터 접근 가능

### RLS (Row Level Security)
- Supabase 데이터베이스 레벨에서 보안 정책 적용
- 사용자별 데이터 접근 제한

## 예제 사용법

### JavaScript (Fetch API)
```javascript
// 로그인
const response = await fetch('/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: 'username=admin&password=0000',
  credentials: 'include'
});

// 업무 로그 생성
const logResponse = await fetch('/api/work_logs', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    work_date: '2024-01-15',
    start_time: '09:00:00',
    end_time: '17:00:00',
    description: '업무 설명'
  }),
  credentials: 'include'
});
```

### Python (requests)
```python
import requests

# 세션 생성
session = requests.Session()

# 로그인
login_data = {
    'username': 'admin',
    'password': '0000'
}
session.post('https://your-app.onrender.com/login', data=login_data)

# 업무 로그 조회
response = session.get('https://your-app.onrender.com/api/work_logs')
logs = response.json()
``` 