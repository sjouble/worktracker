#!/usr/bin/env python3
"""
WorkTracker 데이터베이스 초기화 스크립트
한국시간대(KST) 적용 및 기본 데이터 생성
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from supabase.client import create_client
from dotenv import load_dotenv

# 환경 변수 로드
if os.path.exists('.env'):
    load_dotenv()

# 한국 시간대 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

def get_korean_datetime():
    """한국 시간 기준으로 현재 시간을 반환"""
    return datetime.now(KST)

def init_database():
    """데이터베이스 완전 초기화"""
    print("🔄 WorkTracker 데이터베이스 초기화 시작...")
    
    # Supabase 클라이언트 설정
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase 환경 변수가 설정되지 않았습니다.")
        print("   .env 파일에 SUPABASE_URL과 SUPABASE_KEY를 설정해주세요.")
        return False
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase 연결 성공")
        
        # 1단계: 기존 데이터 삭제
        print("\n📋 1단계: 기존 데이터 삭제 중...")
        
        try:
            # work_logs 삭제
            result = supabase.table('work_logs').delete().neq('id', 0).execute()
            print(f"   ✅ work_logs 데이터 삭제 완료 ({len(result.data) if result.data else 0}개)")
            
            # users 삭제 (admin 제외)
            result = supabase.table('users').delete().neq('username', 'admin').execute()
            print(f"   ✅ users 데이터 삭제 완료 ({len(result.data) if result.data else 0}개)")
            
            # departments 삭제
            result = supabase.table('departments').delete().neq('id', 0).execute()
            print(f"   ✅ departments 데이터 삭제 완료 ({len(result.data) if result.data else 0}개)")
            
        except Exception as e:
            print(f"   ⚠️ 기존 데이터 삭제 중 오류 (무시): {e}")
        
        # 2단계: 기본 데이터 삽입
        print("\n📋 2단계: 기본 데이터 생성 중...")
        
        # departments 삽입
        departments_data = [
            {'name': 'B동보충'},
            {'name': 'A지상보충'},
            {'name': 'A지하보충'}
        ]
        
        for dept in departments_data:
            result = supabase.table('departments').insert(dept).execute()
            print(f"   ✅ 소속 생성: {dept['name']}")
        
        # admin 계정 확인 및 생성
        admin_check = supabase.table('users').select('*').eq('username', 'admin').execute()
        if not admin_check.data:
            admin_data = {
                'username': 'admin',
                'password_hash': '0000',
                'role': 'admin'
            }
            result = supabase.table('users').insert(admin_data).execute()
            print("   ✅ admin 계정 생성 완료")
        else:
            print("   ✅ admin 계정 이미 존재")
        
        # 3단계: 확인
        print("\n📋 3단계: 데이터 확인 중...")
        
        # departments 확인
        dept_result = supabase.table('departments').select('*').execute()
        print(f"   📊 소속 수: {len(dept_result.data)}개")
        for dept in dept_result.data:
            print(f"      - {dept['name']}")
        
        # users 확인
        user_result = supabase.table('users').select('*').execute()
        print(f"   📊 사용자 수: {len(user_result.data)}개")
        for user in user_result.data:
            print(f"      - {user['username']} ({user['role']})")
        
        # work_logs 확인
        task_result = supabase.table('work_logs').select('*').execute()
        print(f"   📊 업무 로그 수: {len(task_result.data)}개")
        
        print(f"\n🎉 데이터베이스 초기화 완료!")
        print(f"   현재 시간 (KST): {get_korean_datetime().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   관리자 계정: admin / 0000")
        print(f"   기본 소속: B동보충, A지상보충, A지하보충")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 WorkTracker 데이터베이스 초기화 도구")
    print("=" * 60)
    
    success = init_database()
    
    if success:
        print("\n✅ 초기화가 성공적으로 완료되었습니다!")
        print("   이제 웹 애플리케이션을 실행하여 사용할 수 있습니다.")
    else:
        print("\n❌ 초기화에 실패했습니다.")
        print("   환경 변수 설정을 확인하고 다시 시도해주세요.")
        sys.exit(1) 