"""
CLI 사용 예제

프롬프트 CRUD CLI의 각 명령어를 사용하는 예제입니다.
"""

import subprocess
import sys
import os

# 공통 설정 (프로젝트 ID는 인증 후 자동으로 설정됨)

print("💡 이 예제를 실행하기 전에 먼저 로그인하세요.")
print("   예: cd C:\\Users\\KOOKYUNGHYUN\\Desktop\\aip-sdk\\cli && python -m adxp_cli.cli auth login")
print("   또는: adxp-cli auth login (패키지가 설치된 경우)")
print("   참고: Python 3.8 호환성 문제로 CLI가 실행되지 않을 수 있습니다.")


def run_cli_command(command):
    """CLI 명령어 실행"""
    print(f"\n{'='*60}")
    print(f"실행 명령어: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Return Code: {result.returncode}")
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        print(f"명령어 실행 실패: {e}")
        return False, "", str(e)


def wait_for_enter(step_name):
    """엔터를 기다리는 함수"""
    print(f"\n{'='*50}")
    print(f"단계 {step_name} 완료!")
    print("다음 단계로 진행하려면 엔터를 누르세요...")
    input()
    print()


def main():
    """CLI 사용 예제 - 단계별 진행"""
    
    print("=== 프롬프트 CRUD CLI 사용 예제 (단계별 진행) ===")
    print("각 단계를 완료한 후 엔터를 눌러 다음 단계로 진행하세요.\n")
    
    # 1. 프롬프트 생성
    print("📝 1단계: 프롬프트 생성")
    print("CLI를 사용해서 프롬프트를 생성합니다...")
    
    create_command = f"""cd C:/Users/KOOKYUNGHYUN/Desktop/aip-sdk/cli && python -m adxp_cli.cli prompts create \
--name "CLI 테스트 프롬프트" \
--description "CLI를 사용해서 생성한 테스트 프롬프트입니다." \
--system-prompt "You are a helpful customer service assistant." \
--user-prompt "안녕하세요, {{name}}님! 오늘은 {{date}}입니다. 무엇을 도와드릴까요?" \
--tags "CLI,테스트,인사" \
--variables "name,date" """
    
    success, stdout, stderr = run_cli_command(create_command)
    
    if success:
        print("✅ 프롬프트 생성 성공!")
        # UUID 추출 (간단한 방법)
        import json
        try:
            # 정규표현식을 사용해서 UUID 추출
            import re
            uuid_pattern = r'"prompt_uuid":\s*"([a-f0-9-]{36})"'
            match = re.search(uuid_pattern, stdout)
            
            if match:
                prompt_uuid = match.group(1)
                print(f"생성된 프롬프트 UUID: {prompt_uuid}")
            else:
                print("⚠️  UUID를 찾을 수 없습니다.")
                print(f"응답 내용: {stdout}")
                prompt_uuid = None
        except Exception as e:
            print(f"⚠️  응답 파싱 실패: {e}")
            print(f"응답 내용: {stdout}")
            prompt_uuid = None
    else:
        print("❌ 프롬프트 생성 실패!")
        prompt_uuid = None
    
    wait_for_enter("1")
    
    # 2. 프롬프트 목록 조회
    print("📋 2단계: 프롬프트 목록 조회")
    print("CLI를 사용해서 프롬프트 목록을 조회합니다...")
    
    list_command = f"""cd C:/Users/KOOKYUNGHYUN/Desktop/aip-sdk/cli && python -m adxp_cli.cli prompts list \
--page 1 \
--size 5"""
    
    success, stdout, stderr = run_cli_command(list_command)
    
    if success:
        print("✅ 프롬프트 목록 조회 성공!")
    else:
        print("❌ 프롬프트 목록 조회 실패!")
    
    wait_for_enter("2")
    
    # 3. 특정 프롬프트 조회 (UUID가 있는 경우만)
    if prompt_uuid:
        print("🔍 3단계: 특정 프롬프트 조회")
        print(f"프롬프트 UUID: {prompt_uuid}")
        print("CLI를 사용해서 특정 프롬프트를 조회합니다...")
        
        get_command = f"""cd C:/Users/KOOKYUNGHYUN/Desktop/aip-sdk/cli && python -m adxp_cli.cli prompts get "{prompt_uuid}" """
        
        success, stdout, stderr = run_cli_command(get_command)
        
        if success:
            print("✅ 프롬프트 조회 성공!")
        else:
            print("❌ 프롬프트 조회 실패!")
    else:
        print("🔍 3단계: 특정 프롬프트 조회 (건너뜀)")
        print("UUID가 없어서 건너뜁니다.")
    
    wait_for_enter("3")
    
    # 4. 프롬프트 수정 (UUID가 있는 경우만)
    if prompt_uuid:
        print("✏️  4단계: 프롬프트 수정")
        print(f"프롬프트 UUID: {prompt_uuid}")
        print("CLI를 사용해서 프롬프트를 수정합니다...")
        
        update_command = f"""cd C:/Users/KOOKYUNGHYUN/Desktop/aip-sdk/cli && python -m adxp_cli.cli prompts update "{prompt_uuid}" \
--name "수정된 CLI 테스트 프롬프트" \
--description "CLI를 사용해서 수정한 테스트 프롬프트입니다." \
--system-prompt "You are a helpful and friendly customer service assistant." \
--user-prompt "안녕하세요, {{name}}님! 오늘은 {{date}}입니다. 무엇을 도와드릴까요? 😊" \
--tags "CLI,테스트,인사,수정됨" \
--variables "name,date" """
        
        success, stdout, stderr = run_cli_command(update_command)
        
        if success:
            print("✅ 프롬프트 수정 성공!")
        else:
            print("❌ 프롬프트 수정 실패!")
    else:
        print("✏️  4단계: 프롬프트 수정 (건너뜀)")
        print("UUID가 없어서 건너뜁니다.")
    
    wait_for_enter("4")
    
    # 5. 프롬프트 삭제 확인 (UUID가 있는 경우만)
    if prompt_uuid:
        print("🗑️  5단계: 프롬프트 삭제")
        print(f"프롬프트 UUID: {prompt_uuid}")
        print("⚠️  실제로 삭제하시겠습니까?")
        print("삭제하려면 'y' 또는 'yes'를 입력하세요:")
        
        delete_choice = input("입력: ").strip()
        
        if delete_choice.lower() in ['y', 'yes']:
            print("CLI를 사용해서 프롬프트를 삭제합니다...")
            
            delete_command = f"""cd C:/Users/KOOKYUNGHYUN/Desktop/aip-sdk/cli && python -m adxp_cli.cli prompts delete "{prompt_uuid}" """
            
            success, stdout, stderr = run_cli_command(delete_command)
            
            if success:
                print("✅ 프롬프트 삭제 성공!")
            else:
                print("❌ 프롬프트 삭제 실패!")
        else:
            print("프롬프트 삭제를 건너뜁니다.")
    else:
        print("🗑️  5단계: 프롬프트 삭제 (건너뜀)")
        print("UUID가 없어서 건너뜁니다.")
    
    wait_for_enter("5")
    
    print("🎉 === 모든 CLI 예제 완료 ===")
    print("프롬프트 CRUD CLI의 모든 기능을 단계별로 확인했습니다!")


if __name__ == "__main__":
    main()
