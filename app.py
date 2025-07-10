from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from supabase.client import create_client, Client
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, date
import uuid
from typing import Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수 로드 (로컬 개발용)
if os.path.exists('.env'):
    load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Supabase 클라이언트 설정
supabase: Optional[Client] = None
try:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("⚠️ Supabase 환경 변수가 설정되지 않았습니다.")
        raise ValueError("SUPABASE_URL과 SUPABASE_KEY가 필요합니다.")
    
    supabase = create_client(supabase_url, supabase_key)
    logger.info("✅ Supabase 연결 성공")
except Exception as e:
    logger.error(f"❌ Supabase 연결 실패: {e}")
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
        
        # Supabase 연결 확인
        if not supabase:
            return render_template('login.html', error="데이터베이스 연결에 문제가 있습니다. 관리자에게 문의하세요.")
        
        try:
            # admin 계정 특별 처리
            if username == 'admin' and password == '0000':
                session['user'] = {
                    'id': 'admin-user-id',
                    'username': 'admin',
                    'role': 'admin'
                }
                logger.info("관리자 로그인 성공")
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
                logger.info(f"사용자 로그인 성공: {username}")
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error="사용자명 또는 비밀번호가 올바르지 않습니다.")
        except Exception as e:
            logger.error(f"로그인 에러: {e}")
            return render_template('login.html', error="로그인에 실패했습니다. 다시 시도해주세요.")
    
    # 세션에서 성공 메시지 가져오기
    success_message = session.pop('success_message', None)
    return render_template('login.html', success=success_message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not supabase:
            return jsonify({'error': 'Supabase 연결이 없습니다.'}), 500
        
        try:
            # 사용자 ID 생성
            user_id = str(uuid.uuid4())
            
            # 사용자 정보 저장
            result = supabase.table('users').insert({
                'id': user_id,
                'username': username,
                'password_hash': password,  # 실제로는 해시화해야 함
                'created_at': datetime.now().isoformat()
            }).execute()
            
            if result.data:
                return jsonify({'success': True, 'message': '회원가입 성공!', 'user_id': user_id})
            else:
                return jsonify({'error': '회원가입 실패'}), 400
                
        except Exception as e:
            logger.error(f"회원가입 에러: {e}")
            return jsonify({'error': f'회원가입 중 오류가 발생했습니다: {str(e)}'}), 500
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    username = session['user']['username']
    
    # Supabase 연결 확인
    if not supabase:
        return render_template('error.html', error="데이터베이스 연결에 문제가 있습니다.")
    
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
        logger.error(f"대시보드 에러: {e}")
        return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    username = session['user']['username']
    
    # Supabase 연결 확인
    if not supabase:
        return render_template('error.html', error="데이터베이스 연결에 문제가 있습니다.")
    
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
        work_logs = supabase.table('work_logs').select('*, users(username)').execute().data
        
        return render_template('admin_dashboard.html', 
                             user={'username': username, 'role': 'admin'},
                             departments=departments,
                             users=users,
                             work_logs=work_logs)
    except Exception as e:
        logger.error(f"관리자 대시보드 에러: {e}")
        return render_template('admin_dashboard.html', 
                             user={'username': username, 'role': 'admin'},
                             departments=[],
                             users=[],
                             work_logs=[])

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