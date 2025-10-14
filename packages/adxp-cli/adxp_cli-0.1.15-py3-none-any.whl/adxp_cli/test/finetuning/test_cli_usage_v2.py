#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Finetuning CRUD CLI V2 - CLI 사용 예제
명령줄에서 트레이닝을 관리하는 방법을 보여줍니다.
"""

import subprocess
import sys
import os
import time
from datetime import datetime


def get_auth_info():
    """
    CLI의 기본 인증 방식을 사용하여 인증 정보를 가져옵니다.
    """
    try:
        # CLI의 저장된 인증 정보 사용
        from adxp_cli.auth.service import get_credential
        headers, config = get_credential()
        
        print("✅ 저장된 인증 정보를 사용합니다.")
        print(f"📋 인증 정보:")
        print(f"   Username: {config.username}")
        print(f"   Project: {config.client_id}")
        print(f"   Base URL: {config.base_url}")
        
        token = config.token
        if not token:
            raise RuntimeError("저장된 토큰을 가져올 수 없습니다.")
        
        print(f"🔑 토큰 정보:")
        print(f"   - 토큰 길이: {len(token)}")
        print(f"   - 토큰 시작: {token[:20]}...")
        
        return token, config.base_url
        
    except Exception as e:
        print(f"❌ 인증 정보 가져오기 실패: {e}")
        print("먼저 'adxp-cli auth login' 명령어로 로그인하세요.")
        return None, None


def run_cli_command(command):
    """CLI 명령어 실행"""
    try:
        print(f"실행 명령어: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 명령어 실행 성공")
            if result.stdout:
                print(f"출력: {result.stdout.strip()}")
            return result.stdout.strip()
        else:
            print(f"❌ 명령어 실행 실패 (코드: {result.returncode})")
            if result.stderr:
                print(f"오류: {result.stderr.strip()}")
            return None
            
    except Exception as e:
        print(f"❌ 명령어 실행 중 오류: {e}")
        return None


def main():
    """CLI 사용 예제 - 단계별 진행"""
    
    print("=== Finetuning CRUD CLI V2 사용 예제 ===")
    print("CLI 명령어로 트레이닝을 관리하는 방법을 보여줍니다.\n")
    
    # 인증 정보 확인
    token, base_url = get_auth_info()
    if not token:
        print("❌ 인증 정보를 가져올 수 없습니다. 먼저 로그인하세요.")
        return
    
    # CLI 메인 파일 경로 (현재 파일에서 3단계 상위로 올라가서 cli.py)
    cli_main = os.path.join(os.path.dirname(__file__), "..", "..", "cli.py")
    if not os.path.exists(cli_main):
        print(f"❌ CLI 파일을 찾을 수 없습니다: {cli_main}")
        return
    
    created_trainings = []  # 생성된 트레이닝들을 추적
    
    # 1. 트레이닝 목록 조회
    print("📋 1단계: 트레이닝 목록 조회")
    print("생성된 트레이닝 목록을 조회합니다...")
    
    try:
        list_command = f'python "{cli_main}" finetuning-v2 list-trainings --limit 5'
        result = run_cli_command(list_command)
        if result:
            print("✅ 트레이닝 목록 조회 성공!")
            print(f"조회 결과: {result}")
        else:
            print("❌ 트레이닝 목록 조회 실패")
    except Exception as e:
        print(f"❌ 트레이닝 목록 조회 실패: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    
    # 2. 트레이닝 생성
    print("\n📝 2단계: 트레이닝 생성")
    print("테스트 트레이닝을 생성합니다...")
    
    try:
        # 테스트 트레이닝 데이터 (실제 ID 사용, Windows CMD 호환 방식)
        training_name = f"cli-training-v2-{int(time.time())}"
        
        # Windows CMD에서 작동하는 방식으로 명령어 구성
        create_command = f'python "{cli_main}" finetuning-v2 create-training --name "{training_name}" --project_id "24ba585a-02fc-43d8-b9f1-f7ca9e020fe5" --task_id "b73964a0-dd51-410c-b20e-30ea293eb019" --trainer_id "77a85f64-5717-4562-b3fc-2c963f66afa6" --dataset_ids "[\\"0c178ea6-fbc9-44f2-8b1e-6bb101901a8c\\"]" --base_model_id "cb0a4bdb-d2d6-48b3-98a3-b6333484329f" --resource "{{\\"cpu_quota\\": 4, \\"mem_quota\\": 8, \\"gpu_quota\\": 1, \\"gpu_type\\": \\"T4\\"}}" --params "learning_rate=0.0001" --description "CLI V2로 생성한 테스트 트레이닝"'
        
        result = run_cli_command(create_command)
        if result:
            # JSON 파싱 시도 (디버그 메시지 제거)
            try:
                import json
                # 마지막 JSON 블록 찾기 (가장 완전한 JSON)
                lines = result.split('\n')
                json_lines = []
                in_json = False
                
                for line in lines:
                    if line.strip().startswith('{'):
                        in_json = True
                        json_lines = [line]
                    elif in_json:
                        json_lines.append(line)
                        if line.strip().endswith('}'):
                            break
                
                if json_lines:
                    json_content = '\n'.join(json_lines)
                    training_info = json.loads(json_content)
                    training_id = training_info.get('id')
                    if training_id:
                        print(f"✅ 트레이닝 생성 성공!")
                        print(f"Training ID: {training_id}")
                        created_trainings.append(("Test Training", training_id))
                    else:
                        print("❌ Training ID를 찾을 수 없습니다.")
                else:
                    print("❌ JSON 응답을 찾을 수 없습니다.")
            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 실패: {e}")
                # 간단한 방법으로 ID 추출 시도
                if '"id":' in result:
                    import re
                    id_match = re.search(r'"id":\s*"([^"]+)"', result)
                    if id_match:
                        training_id = id_match.group(1)
                        print(f"✅ 트레이닝 생성 성공! (정규식으로 추출)")
                        print(f"Training ID: {training_id}")
                        created_trainings.append(("Test Training", training_id))
                    else:
                        print("❌ Training ID를 찾을 수 없습니다.")
                else:
                    print("❌ JSON 응답을 찾을 수 없습니다.")
        else:
            print("❌ 트레이닝 생성 실패")
    except Exception as e:
        print(f"❌ 트레이닝 생성 실패: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    
    # 3. 트레이닝 상세 조회
    print("\n🔍 3단계: 트레이닝 상세 조회")
    if created_trainings:
        training_name, training_id = created_trainings[0]
        print(f"{training_name}의 상세 정보를 조회합니다...")
        
        try:
            get_command = f'python "{cli_main}" finetuning-v2 get-training "{training_id}"'
            result = run_cli_command(get_command)
            if result:
                print("✅ 트레이닝 상세 조회 성공!")
                print(f"상세 정보: {result}")
            else:
                print("❌ 트레이닝 상세 조회 실패")
        except Exception as e:
            print(f"❌ 트레이닝 상세 조회 실패: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("조회할 트레이닝이 없습니다.")
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    
    # 4. 트레이닝 수정
    print("\n✏️ 4단계: 트레이닝 수정")
    if created_trainings:
        training_name, training_id = created_trainings[0]
        print(f"{training_name}의 정보를 수정합니다...")
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_command = f'python "{cli_main}" finetuning-v2 update-training "{training_id}" --description "수정된 설명 - {timestamp}" --params "learning_rate=0.0005\\nepochs=10\\nbatch_size=16"'
            result = run_cli_command(update_command)
            if result:
                print("✅ 트레이닝 수정 성공!")
                print(f"수정 결과: {result}")
            else:
                print("❌ 트레이닝 수정 실패")
        except Exception as e:
            print(f"❌ 트레이닝 수정 실패: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("수정할 트레이닝이 없습니다.")
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    
    # 5. 트레이닝 로그 조회
    print("\n📊 5단계: 트레이닝 로그 조회")
    if created_trainings:
        training_name, training_id = created_trainings[0]
        print(f"{training_name}의 로그를 조회합니다...")
        
        try:
            logs_command = f'python "{cli_main}" finetuning-v2 get-logs "{training_id}" --limit 10'
            result = run_cli_command(logs_command)
            if result:
                print("✅ 트레이닝 로그 조회 성공!")
                print(f"로그 결과: {result}")
            else:
                print("❌ 트레이닝 로그 조회 실패")
        except Exception as e:
            print(f"❌ 트레이닝 로그 조회 실패: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("조회할 트레이닝이 없습니다.")
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    
    # 6. 트레이닝 시작
    print("\n🚀 6단계: 트레이닝 시작")
    if created_trainings:
        training_name, training_id = created_trainings[0]
        print(f"{training_name}을 시작합니다...")
        
        try:
            start_command = f'python "{cli_main}" finetuning-v2 start-training "{training_id}"'
            result = run_cli_command(start_command)
            if result:
                print("✅ 트레이닝 시작 성공!")
                print(f"시작 결과: {result}")
            else:
                print("❌ 트레이닝 시작 실패")
        except Exception as e:
            print(f"❌ 트레이닝 시작 실패: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("시작할 트레이닝이 없습니다.")
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    
    # 7. 트레이닝 중지
    print("\n⏹️ 7단계: 트레이닝 중지")
    if created_trainings:
        training_name, training_id = created_trainings[0]
        print(f"{training_name}을 중지합니다...")
        
        try:
            stop_command = f'python "{cli_main}" finetuning-v2 stop-training "{training_id}"'
            result = run_cli_command(stop_command)
            if result:
                print("✅ 트레이닝 중지 성공!")
                print(f"중지 결과: {result}")
            else:
                print("❌ 트레이닝 중지 실패")
        except Exception as e:
            print(f"❌ 트레이닝 중지 실패: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("중지할 트레이닝이 없습니다.")
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    
    # 8. 트레이닝 메트릭 조회
    print("\n📈 8단계: 트레이닝 메트릭 조회")
    if created_trainings:
        training_name, training_id = created_trainings[0]
        print(f"{training_name}의 메트릭을 조회합니다...")
        
        try:
            metrics_command = f'python "{cli_main}" finetuning-v2 get-metrics "{training_id}"'
            result = run_cli_command(metrics_command)
            if result:
                print("✅ 트레이닝 메트릭 조회 성공!")
                print(f"메트릭 결과: {result}")
            else:
                print("❌ 트레이닝 메트릭 조회 실패")
        except Exception as e:
            print(f"❌ 트레이닝 메트릭 조회 실패: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("조회할 트레이닝이 없습니다.")
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    
    # 9. 생성된 트레이닝들 삭제 여부 확인
    print("\n🗑️ 9단계: 트레이닝 삭제")
    if created_trainings:
        print("생성된 트레이닝 목록:")
        for i, (name, training_id) in enumerate(created_trainings, 1):
            print(f"  {i}. {name}: {training_id}")
        
        print(f"\n총 {len(created_trainings)}개의 트레이닝이 생성되었습니다.")
        delete_choice = input("생성된 트레이닝들을 삭제하시겠습니까? (y/N): ").strip().lower()
        
        if delete_choice in ['y', 'yes']:
            print("\n🗑️  트레이닝 삭제 중...")
            for name, training_id in created_trainings:
                try:
                    delete_command = f'python "{cli_main}" finetuning-v2 delete-training "{training_id}"'
                    result = run_cli_command(delete_command)
                    if result:
                        print(f"✅ {name} 트레이닝 삭제 완료: {training_id}")
                    else:
                        print(f"❌ {name} 트레이닝 삭제 실패")
                except Exception as e:
                    print(f"❌ {name} 트레이닝 삭제 실패: {e}")
            print("✅ 모든 트레이닝 삭제가 완료되었습니다!")
        else:
            print("트레이닝 삭제를 건너뛰었습니다.")
    else:
        print("삭제할 트레이닝이 없습니다.")
    
    print("\n🎉 모든 단계가 완료되었습니다!")
    print("Finetuning CRUD CLI V2 사용 예제를 마칩니다.")


if __name__ == "__main__":
    main()
