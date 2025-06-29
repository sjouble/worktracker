from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from supabase.client import create_client, Client
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Supabase 클라이언트 설정
supabase: Client = create_client(
    os.getenv('SUPABASE_URL') or '',
    os.getenv('SUPABASE_KEY') or ''
)

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
                    'username': 'admin'
                }
                return redirect(url_for('dashboard'))
            
            # 일반 사용자 로그인 (사용자명만 확인)
            user_data = supabase.table('users').select('*').eq('username', username).execute()
            
            if user_data.data:
                # 실제 구현에서는 비밀번호 해시 검증이 필요합니다
                # 여기서는 간단히 사용자명만 확인
                session['user'] = {
                    'id': user_data.data[0]['id'],
                    'username': user_data.data[0]['username']
                }
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error="사용자명 또는 비밀번호가 올바르지 않습니다.")
        except Exception as e:
            print(f"로그인 에러: {e}")  # 디버깅용
            return render_template('login.html', error="로그인에 실패했습니다. 다시 시도해주세요.")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        department_id = request.form['department']
        
        # 비밀번호 재확인 검증
        if password != confirm_password:
            return render_template('register.html', error="비밀번호가 일치하지 않습니다.")
        
        # 비밀번호 길이 검증
        if len(password) < 6:
            return render_template('register.html', error="비밀번호는 최소 6자 이상이어야 합니다.")
        
        # 소속 선택 검증
        if not department_id:
            return render_template('register.html', error="소속을 선택해주세요.")
        
        try:
            # 사용자명 중복 확인
            existing_user = supabase.table('users').select('*').eq('username', username).execute()
            
            if existing_user.data:
                return render_template('register.html', error="이미 존재하는 사용자명입니다.")
            
            # UUID 생성 (간단한 방법)
            user_id = str(uuid.uuid4())
            
            # users 테이블에 사용자 정보 저장 (Supabase 인증 없이)
            supabase.table('users').insert({
                'id': user_id,
                'username': username,
                'role': 'user',
                'department_id': int(department_id)
            }).execute()
            
            return render_template('login.html', success="회원가입이 완료되었습니다. 로그인해주세요.")
        except Exception as e:
            print(f"회원가입 에러: {e}")  # 디버깅용
            return render_template('register.html', error="회원가입에 실패했습니다. 다시 시도해주세요.")
    
    # departments 조회 시 에러 처리 추가
    try:
        departments = supabase.table('departments').select('*').execute().data
    except Exception as e:
        # RLS 정책 문제로 departments 조회 실패 시 기본 데이터 사용
        departments = [
            {'id': 1, 'name': 'B동입고'},
            {'id': 2, 'name': 'A지상보충'},
            {'id': 3, 'name': 'A지하보충'}
        ]
    
    return render_template('register.html', departments=departments)

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
    
    return render_template('admin_dashboard.html', user={'username': username, 'role': 'admin'})

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