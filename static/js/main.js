// 전역 변수
let currentTaskId = null;

// 업무 저장 함수
async function saveTask() {
    const taskType = document.getElementById('taskType').value;
    const description = document.getElementById('description').value;
    const status = document.getElementById('status').value;
    const startTime = document.getElementById('startTime').value;
    const endTime = document.getElementById('endTime').value;

    if (!taskType || !status || !startTime) {
        alert('필수 항목을 모두 입력해주세요.');
        return;
    }

    const taskData = {
        task_type: taskType,
        description: description,
        status: status,
        start_time: startTime,
        end_time: endTime || null
    };

    try {
        const url = currentTaskId ? `/api/tasks/${currentTaskId}` : '/api/tasks';
        const method = currentTaskId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData)
        });

        if (response.ok) {
            location.reload();
        } else {
            const error = await response.json();
            alert(error.error || '업무 저장에 실패했습니다.');
        }
    } catch (error) {
        alert('업무 저장 중 오류가 발생했습니다.');
    }
}

// 업무 수정 함수
function editTask(taskId) {
    currentTaskId = taskId;
    const row = document.querySelector(`tr[data-task-id="${taskId}"]`);
    const cells = row.cells;

    document.getElementById('taskType').value = cells[0].textContent;
    document.getElementById('description').value = cells[1].textContent;
    document.getElementById('status').value = cells[2].querySelector('.badge').textContent.trim();
    document.getElementById('startTime').value = formatDateTimeForInput(cells[3].textContent);
    document.getElementById('endTime').value = formatDateTimeForInput(cells[4].textContent);

    document.getElementById('taskModalTitle').textContent = '업무 수정';
    new bootstrap.Modal(document.getElementById('taskModal')).show();
}

// 업무 삭제 함수
async function deleteTask(taskId) {
    if (!confirm('정말로 이 업무를 삭제하시겠습니까?')) {
        return;
    }

    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            location.reload();
        } else {
            const error = await response.json();
            alert(error.error || '업무 삭제에 실패했습니다.');
        }
    } catch (error) {
        alert('업무 삭제 중 오류가 발생했습니다.');
    }
}



// 날짜 시간 형식 변환 함수
function formatDateTimeForInput(dateTimeString) {
    if (!dateTimeString || dateTimeString === 'None') {
        return '';
    }
    
    const date = new Date(dateTimeString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

// 모달 초기화
document.addEventListener('DOMContentLoaded', function() {
    const taskModal = document.getElementById('taskModal');
    if (taskModal) {
        taskModal.addEventListener('hidden.bs.modal', function() {
            // 모달이 닫힐 때 폼 초기화
            document.getElementById('taskForm').reset();
            currentTaskId = null;
            document.getElementById('taskModalTitle').textContent = '새 업무 등록';
        });
    }
}); 