#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dataset CRUD CLI - CLI 사용 예제
명령줄에서 Dataset을 관리하는 방법을 보여줍니다.
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


def get_files_path():
    """files 디렉토리 경로 반환"""
    return os.path.join(os.path.dirname(__file__), "files")


def main():
    """CLI 사용 예제 - 단계별 진행"""
    
    print("=== Dataset CRUD CLI 사용 예제 ===")
    print("CLI 명령어로 Dataset을 관리하는 방법을 보여줍니다.\n")
    
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
    
    created_datasets = []  # 생성된 Dataset들을 추적
    
    # 1. Supervised Finetuning Dataset 생성
    print("📝 1단계: Supervised Finetuning Dataset 생성")
    print("Supervised Finetuning Dataset을 생성합니다...")
    
    try:
        supervised_file = os.path.join(get_files_path(), 'supervised_data.csv')
        if os.path.exists(supervised_file):
            # CLI 명령어 구성
            create_command = f'python "{cli_main}" dataset create --name "cli_supervised_{int(time.time())}" --project-id "24ba585a-02fc-43d8-b9f1-f7ca9e020fe5" --description "CLI 예제 - Supervised Finetuning Dataset" --dataset-type "supervised_finetuning" --files "{supervised_file}" --tags "basic_usage,supervised,test"'
            
            result = run_cli_command(create_command)
            if result:
                # Dataset ID 추출 시도
                try:
                    import re
                    # "Dataset 생성 성공: {id}" 패턴에서 ID 추출
                    success_pattern = r'Dataset 생성 성공: ([a-f0-9-]+)'
                    match = re.search(success_pattern, result)
                    if match:
                        dataset_id = match.group(1)
                        print(f"✅ Supervised Dataset 생성 성공!")
                        print(f"Dataset ID: {dataset_id}")
                        created_datasets.append(("Supervised", dataset_id))
                    else:
                        # JSON 파싱 시도 (fallback)
                        import json
                        json_start = result.find('{')
                        if json_start != -1:
                            json_content = result[json_start:]
                            dataset_info = json.loads(json_content)
                            dataset_id = dataset_info.get('id')
                            if dataset_id:
                                print(f"✅ Supervised Dataset 생성 성공!")
                                print(f"Dataset ID: {dataset_id}")
                                created_datasets.append(("Supervised", dataset_id))
                            else:
                                print("❌ Dataset ID를 찾을 수 없습니다.")
                        else:
                            print("❌ Dataset ID를 찾을 수 없습니다.")
                except Exception as e:
                    print(f"❌ ID 추출 실패: {e}")
                    print(f"원본 응답: {result}")
        else:
            print("❌ supervised_data.csv 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ Supervised Dataset 생성 실패: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    
    # 2. Unsupervised Finetuning Dataset 생성
    print("\n📝 2단계: Unsupervised Finetuning Dataset 생성")
    print("Unsupervised Finetuning Dataset을 생성합니다...")
    
    try:
        unsupervised_file = os.path.join(get_files_path(), 'unsupervised_data.csv')
        if os.path.exists(unsupervised_file):
            # CLI 명령어 구성 (auth login으로 인증된 상태에서 실행)
            create_command = f'python "{cli_main}" dataset create --name "cli_unsupervised_{int(time.time())}" --project-id "24ba585a-02fc-43d8-b9f1-f7ca9e020fe5" --description "CLI 예제 - Unsupervised Finetuning Dataset" --dataset-type "unsupervised_finetuning" --files "{unsupervised_file}" --tags "basic_usage,unsupervised,test"'
            
            result = run_cli_command(create_command)
            if result:
                # Dataset ID 추출 시도
                try:
                    import re
                    # "Dataset 생성 성공: {id}" 패턴에서 ID 추출
                    success_pattern = r'Dataset 생성 성공: ([a-f0-9-]+)'
                    match = re.search(success_pattern, result)
                    if match:
                        dataset_id = match.group(1)
                        print(f"✅ Unsupervised Dataset 생성 성공!")
                        print(f"Dataset ID: {dataset_id}")
                        created_datasets.append(("Unsupervised", dataset_id))
                    else:
                        # JSON 파싱 시도 (fallback)
                        import json
                        json_start = result.find('{')
                        if json_start != -1:
                            json_content = result[json_start:]
                            dataset_info = json.loads(json_content)
                            dataset_id = dataset_info.get('id')
                            if dataset_id:
                                print(f"✅ Unsupervised Dataset 생성 성공!")
                                print(f"Dataset ID: {dataset_id}")
                                created_datasets.append(("Unsupervised", dataset_id))
                            else:
                                print("❌ Dataset ID를 찾을 수 없습니다.")
                        else:
                            print("❌ Dataset ID를 찾을 수 없습니다.")
                except Exception as e:
                    print(f"❌ ID 추출 실패: {e}")
                    print(f"원본 응답: {result}")
        else:
            print("❌ unsupervised_data.csv 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ Unsupervised Dataset 생성 실패: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    
    # 3. Dataset 목록 조회
    print("\n📋 3단계: Dataset 목록 조회")
    print("생성된 Dataset 목록을 조회합니다...")
    
    try:
        list_command = f'python "{cli_main}" dataset list --project-id "24ba585a-02fc-43d8-b9f1-f7ca9e020fe5" --page 1 --size 10'
        result = run_cli_command(list_command)
        if result:
            print("✅ Dataset 목록 조회 성공!")
            print(f"조회 결과: {result}")
        else:
            print("❌ Dataset 목록 조회 실패")
    except Exception as e:
        print(f"❌ Dataset 목록 조회 실패: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    # 4. Dataset 상세 조회
    print("\n🔍 4단계: Dataset 상세 조회")
    if created_datasets:
        dataset_name, dataset_id = created_datasets[0]
        print(f"{dataset_name} Dataset의 상세 정보를 조회합니다...")
        
        try:
            get_command = f'python "{cli_main}" dataset get "{dataset_id}"'
            result = run_cli_command(get_command)
            if result:
                print("✅ Dataset 상세 조회 성공!")
                print(f"상세 정보: {result}")
            else:
                print("❌ Dataset 상세 조회 실패")
        except Exception as e:
            print(f"❌ Dataset 상세 조회 실패: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("조회할 Dataset이 없습니다.")
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    
    # 5. Dataset 수정
    print("\n✏️ 5단계: Dataset 수정")
    if created_datasets:
        dataset_name, dataset_id = created_datasets[0]
        print(f"{dataset_name} Dataset의 설명을 수정합니다...")
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_command = f'python "{cli_main}" dataset update "{dataset_id}" --description "수정된 설명 - {timestamp}" --project-id "24ba585a-02fc-43d8-b9f1-f7ca9e020fe5"'
            result = run_cli_command(update_command)
            if result:
                print("✅ Dataset 수정 성공!")
                print(f"수정 결과: {result}")
            else:
                print("❌ Dataset 수정 실패")
        except Exception as e:
            print(f"❌ Dataset 수정 실패: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("수정할 Dataset이 없습니다.")
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    
    # 6. Dataset 태그 수정
    print("\n🏷️ 6단계: Dataset 태그 수정")
    if created_datasets:
        dataset_name, dataset_id = created_datasets[0]
        print(f"{dataset_name} Dataset의 태그를 수정합니다...")
        
        try:
            tags_command = f'python "{cli_main}" dataset update-tags "{dataset_id}" --tags "수정됨,basic_usage,업데이트,태그수정"'
            result = run_cli_command(tags_command)
            if result:
                print("✅ Dataset 태그 수정 성공!")
                print(f"태그 수정 결과: {result}")
            else:
                print("❌ Dataset 태그 수정 실패")
        except Exception as e:
            print(f"❌ Dataset 태그 수정 실패: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("수정할 Dataset이 없습니다.")
    
    input("\nEnter를 눌러서 다음 단계로 진행하세요...")
    
    # 7. 생성된 Dataset들 삭제 여부 확인
    print("\n🗑️ 7단계: Dataset 삭제")
    if created_datasets:
        print("생성된 Dataset 목록:")
        for i, (name, dataset_id) in enumerate(created_datasets, 1):
            print(f"  {i}. {name}: {dataset_id}")
        
        print(f"\n총 {len(created_datasets)}개의 Dataset이 생성되었습니다.")
        delete_choice = input("생성된 Dataset들을 삭제하시겠습니까? (y/N): ").strip().lower()
        
        if delete_choice in ['y', 'yes']:
            print("\n🗑️  Dataset 삭제 중...")
            for name, dataset_id in created_datasets:
                try:
                    # 자동 확인을 위해 echo y | 사용
                    delete_command = f'echo y | python "{cli_main}" dataset delete "{dataset_id}"'
                    result = run_cli_command(delete_command)
                    if result:
                        print(f"✅ {name} Dataset 삭제 완료: {dataset_id}")
                    else:
                        print(f"❌ {name} Dataset 삭제 실패")
                except Exception as e:
                    print(f"❌ {name} Dataset 삭제 실패: {e}")
            print("✅ 모든 Dataset 삭제가 완료되었습니다!")
        else:
            print("Dataset 삭제를 건너뛰었습니다.")
    else:
        print("삭제할 Dataset이 없습니다.")
    
    print("\n🎉 모든 단계가 완료되었습니다!")
    print("Dataset CRUD CLI 사용 예제를 마칩니다.")


if __name__ == "__main__":
    main()