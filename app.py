from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# Supabase 클라이언트 설정
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            session['user'] = response.user
            return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('login.html', error="로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        
        try:
            # 사용자 생성
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            # users 테이블에 추가 정보 저장
            supabase.table('users').insert({
                'id': response.user.id,
                'username': username,
                'role': 'user'
            }).execute()
            
            return render_template('login.html', success="회원가입이 완료되었습니다. 로그인해주세요.")
        except Exception as e:
            return render_template('register.html', error="회원가입에 실패했습니다. 다시 시도해주세요.")
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    
    try:
        # 사용자 역할 확인
        user_data = supabase.table('users').select('*').eq('id', user_id).execute()
        role = user_data.data[0]['role'] if user_data.data else 'user'
        
        if role == 'admin':
            # 관리자: 모든 업무 조회
            tasks = supabase.table('tasks').select('*, users(username)').execute()
        else:
            # 일반 사용자: 본인 업무만 조회
            tasks = supabase.table('tasks').select('*').eq('assigned_to', user_id).execute()
        
        return render_template('dashboard.html', tasks=tasks.data, role=role, username=user_data.data[0]['username'])
    except Exception as e:
        return render_template('dashboard.html', tasks=[], role='user', error="데이터를 불러오는데 실패했습니다.")

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    if 'user' not in session:
        return jsonify({'error': '로그인이 필요합니다'}), 401
    
    user_id = session['user']['id']
    
    try:
        # 사용자 역할 확인
        user_data = supabase.table('users').select('*').eq('id', user_id).execute()
        role = user_data.data[0]['role'] if user_data.data else 'user'
        
        if role == 'admin':
            # 관리자: 모든 업무 조회
            tasks = supabase.table('tasks').select('*, users(username)').execute()
        else:
            # 일반 사용자: 본인 업무만 조회
            tasks = supabase.table('tasks').select('*').eq('assigned_to', user_id).execute()
        
        return jsonify(tasks.data)
    except Exception as e:
        return jsonify({'error': '업무 목록을 불러오는데 실패했습니다.'}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    if 'user' not in session:
        return jsonify({'error': '로그인이 필요합니다'}), 401
    
    data = request.json
    user_id = session['user']['id']
    
    try:
        task_data = {
            'task_type': data['task_type'],
            'description': data['description'],
            'status': data['status'],
            'assigned_to': user_id,
            'start_time': data['start_time'],
            'end_time': data['end_time']
        }
        
        result = supabase.table('tasks').insert(task_data).execute()
        
        # 로그 기록
        supabase.table('logs').insert({
            'user_id': user_id,
            'action': '업무 생성',
            'timestamp': datetime.now().isoformat()
        }).execute()
        
        return jsonify(result.data[0])
    except Exception as e:
        return jsonify({'error': '업무 생성에 실패했습니다.'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if 'user' not in session:
        return jsonify({'error': '로그인이 필요합니다'}), 401
    
    data = request.json
    user_id = session['user']['id']
    
    try:
        # 권한 확인
        task = supabase.table('tasks').select('*').eq('id', task_id).execute()
        if not task.data:
            return jsonify({'error': '업무를 찾을 수 없습니다'}), 404
        
        user_data = supabase.table('users').select('*').eq('id', user_id).execute()
        role = user_data.data[0]['role'] if user_data.data else 'user'
        
        if role != 'admin' and task.data[0]['assigned_to'] != user_id:
            return jsonify({'error': '권한이 없습니다'}), 403
        
        result = supabase.table('tasks').update(data).eq('id', task_id).execute()
        
        # 로그 기록
        supabase.table('logs').insert({
            'user_id': user_id,
            'action': '업무 수정',
            'timestamp': datetime.now().isoformat()
        }).execute()
        
        return jsonify(result.data[0])
    except Exception as e:
        return jsonify({'error': '업무 수정에 실패했습니다.'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if 'user' not in session:
        return jsonify({'error': '로그인이 필요합니다'}), 401
    
    user_id = session['user']['id']
    
    try:
        # 권한 확인
        task = supabase.table('tasks').select('*').eq('id', task_id).execute()
        if not task.data:
            return jsonify({'error': '업무를 찾을 수 없습니다'}), 404
        
        user_data = supabase.table('users').select('*').eq('id', user_id).execute()
        role = user_data.data[0]['role'] if user_data.data else 'user'
        
        if role != 'admin' and task.data[0]['assigned_to'] != user_id:
            return jsonify({'error': '권한이 없습니다'}), 403
        
        supabase.table('tasks').delete().eq('id', task_id).execute()
        
        # 로그 기록
        supabase.table('logs').insert({
            'user_id': user_id,
            'action': '업무 삭제',
            'timestamp': datetime.now().isoformat()
        }).execute()
        
        return jsonify({'message': '업무가 삭제되었습니다.'})
    except Exception as e:
        return jsonify({'error': '업무 삭제에 실패했습니다.'}), 500

@app.route('/api/export')
def export_excel():
    if 'user' not in session:
        return jsonify({'error': '로그인이 필요합니다'}), 401
    
    user_id = session['user']['id']
    
    try:
        # 사용자 역할 확인
        user_data = supabase.table('users').select('*').eq('id', user_id).execute()
        role = user_data.data[0]['role'] if user_data.data else 'user'
        
        if role == 'admin':
            # 관리자: 모든 업무 조회
            tasks = supabase.table('tasks').select('*, users(username)').execute()
        else:
            # 일반 사용자: 본인 업무만 조회
            tasks = supabase.table('tasks').select('*').eq('assigned_to', user_id).execute()
        
        # DataFrame 생성
        df = pd.DataFrame(tasks.data)
        
        # Excel 파일 생성
        filename = f"worktracker_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join('static', 'exports', filename)
        
        # exports 폴더가 없으면 생성
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        df.to_excel(filepath, index=False)
        
        return jsonify({'filename': filename, 'message': '엑셀 파일이 생성되었습니다.'})
    except Exception as e:
        return jsonify({'error': '엑셀 파일 생성에 실패했습니다.'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    if 'user' not in session:
        return jsonify({'error': '로그인이 필요합니다'}), 401
    
    try:
        filepath = os.path.join('static', 'exports', filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': '파일 다운로드에 실패했습니다.'}), 500

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True) 