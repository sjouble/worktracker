from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from supabase.client import create_client, Client
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import uuid
from typing import Optional

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Supabase 클라이언트 설정
supabase: Optional[Client] = None
try:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("⚠️ Supabase 환경 변수가 설정되지 않았습니다.")
        supabase_url = 'https://cnooukcuxxqgfiuvrmuk.supabase.co'
        supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNub291a2N1eHhxZ2ZpdXZybXVrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTExMzI5MzQsImV4cCI6MjA2NjcwODkzNH0.GPLp7y2BTXKI6kY7sd_9KEeZD-l1KqR4dMavZjD2_Qc'
    
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Supabase 연결 성공")
except Exception as e:
    print(f"❌ Supabase 연결 실패: {e}")
    supabase = None

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'WorkTracker is running'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Page not found'}), 404

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            # admin 계정 특별 처리
            if username == 'admin' and password == '0000':
                session['user'] = {
                    'id': 'admin-user-id',
                    'username': 'admin',
                    'role': 'admin'
                }
                print("관리자 로그인 성공")  # 디버깅용
                return redirect(url_for('admin_dashboard'))
            
            # 일반 사용자 로그인 (사용자명만 확인)
            user_data = supabase.table('users').select('*').eq('username', username).execute()
            
            if user_data.data:
                # 실제 구현에서는 비밀번호 해시 검증이 필요합니다
                # 여기서는 간단히 사용자명만 확인
                session['user'] = {
                    'id': user_data.data[0]['id'],
                    'username': user_data.data[0]['username']
                }
                print(f"사용자 로그인 성공: {username}")  # 디버깅용
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error="사용자명 또는 비밀번호가 올바르지 않습니다.")
        except Exception as e:
            print(f"로그인 에러: {e}")  # 디버깅용
            return render_template('login.html', error="로그인에 실패했습니다. 다시 시도해주세요.")
    
    # 세션에서 성공 메시지 가져오기
    success_message = session.pop('success_message', None)
    return render_template('login.html', success=success_message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if not supabase:
            return jsonify({'error': 'Supabase 연결이 없습니다.'}), 500
        
        try:
            # 사용자 ID 생성
            user_id = str(uuid.uuid4())
            
            # 사용자 정보 저장
            result = supabase.table('users').insert({
                'id': user_id,
                'username': username,
                'email': email,
                'password': password,  # 실제로는 해시화해야 함
                'created_at': datetime.now().isoformat()
            }).execute()
            
            if result.data:
                return jsonify({'success': True, 'message': '회원가입 성공!', 'user_id': user_id})
            else:
                return jsonify({'error': '회원가입 실패'}), 400
                
        except Exception as e:
            print(f"회원가입 에러: {e}")
            return jsonify({'error': f'회원가입 중 오류가 발생했습니다: {str(e)}'}), 500
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    username = session['user']['username']
    
    try:
        # 관리자 계정 특별 처리
        if username == 'admin':
            return render_template('admin_dashboard.html', user={'username': 'admin', 'role': 'admin'})
        
        # 일반 사용자 정보와 소속 정보를 함께 조회
        user_info = supabase.table('users').select('*, departments(name)').eq('id', user_id).execute()
        
        if user_info.data:
            user = user_info.data[0]
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'department_id': user['department_id'],
                'department_name': user['departments']['name'] if user['departments'] else None,
                'created_at': user['created_at']
            }
            
            if user['role'] == 'admin':
                return render_template('admin_dashboard.html', user=user_data)
            else:
                return render_template('dashboard.html', user=user_data)
        else:
            return redirect(url_for('login'))
    except Exception as e:
        return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    username = session['user']['username']
    
    # 관리자 권한 확인
    if username != 'admin':
        try:
            user_info = supabase.table('users').select('*').eq('id', user_id).execute()
            if not user_info.data or user_info.data[0]['role'] != 'admin':
                return redirect(url_for('dashboard'))
        except:
            return redirect(url_for('dashboard'))
    
    try:
        # 관리자용 데이터 로드
        departments = supabase.table('departments').select('*').execute().data
        users = supabase.table('users').select('*, departments(name)').execute().data
        tasks = supabase.table('tasks').select('*, users(username)').execute().data
        
        return render_template('admin_dashboard.html', 
                             user={'username': username, 'role': 'admin'},
                             departments=departments,
                             users=users,
                             tasks=tasks)
    except Exception as e:
        print(f"관리자 대시보드 에러: {e}")
        return render_template('admin_dashboard.html', 
                             user={'username': username, 'role': 'admin'},
                             departments=[],
                             users=[],
                             tasks=[])

@app.route('/test')
def test():
    return jsonify({'message': 'Test endpoint working!', 'status': 'success'})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 