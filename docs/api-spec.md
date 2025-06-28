# WorkTracker API 명세서

## 인증
모든 API 엔드포인트는 로그인된 사용자만 접근 가능합니다.

## 엔드포인트

### 1. 업무 관리

#### GET /api/tasks
업무 목록을 조회합니다.

**응답:**
```json
[
  {
    "id": 1,
    "task_type": "인출",
    "description": "상품 인출 작업",
    "status": "진행중",
    "assigned_to": "user-uuid",
    "start_time": "2024-01-01T09:00:00",
    "end_time": "2024-01-01T17:00:00",
    "created_at": "2024-01-01T09:00:00"
  }
]
```

#### POST /api/tasks
새 업무를 생성합니다.

**요청 본문:**
```json
{
  "task_type": "인출",
  "description": "상품 인출 작업",
  "status": "진행중",
  "start_time": "2024-01-01T09:00:00",
  "end_time": "2024-01-01T17:00:00"
}
```

#### PUT /api/tasks/{task_id}
업무를 수정합니다.

**요청 본문:**
```json
{
  "task_type": "완료",
  "description": "상품 인출 작업 완료",
  "status": "완료",
  "start_time": "2024-01-01T09:00:00",
  "end_time": "2024-01-01T17:00:00"
}
```

#### DELETE /api/tasks/{task_id}
업무를 삭제합니다.

### 2. 엑셀 내보내기

#### GET /api/export
업무 목록을 엑셀 파일로 내보냅니다.

**응답:**
```json
{
  "filename": "worktracker_export_20240101_120000.xlsx",
  "message": "엑셀 파일이 생성되었습니다."
}
```

#### GET /download/{filename}
생성된 엑셀 파일을 다운로드합니다.

## 오류 응답

```json
{
  "error": "오류 메시지"
}
```

## 상태 코드

- 200: 성공
- 401: 인증 필요
- 403: 권한 없음
- 404: 리소스를 찾을 수 없음
- 500: 서버 오류 