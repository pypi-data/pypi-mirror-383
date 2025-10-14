# import subprocess
# import sys
# import time
# import pytest
# import tempfile
# import os
# import zipfile
# import json
# import re
# import random
# import click
# import ast

# def run_cli_command(args, input_text=None):
#     cmd = [sys.executable, '-m', 'adxp_cli.model.cli'] + args
#     result = subprocess.run(cmd, capture_output=True, text=True, input=input_text)
#     print(f"\n[STDOUT]\n{result.stdout}\n[STDERR]\n{result.stderr}")
#     return result

# def generate_random_name(prefix):
#     return f"{prefix}_{random.randint(100000, 999999)}"

# def extract_id_from_output(output):
#     import re
#     match = re.search(r"'id': '([\w-]+)'", output)
#     if match:
#         return match.group(1)
#     match = re.search(r'"id"\s*:\s*"([\w-]+)"', output)
#     if match:
#         return match.group(1)
#     # 표 형태(tabulate)에서 id 추출 (UUID 패턴만)
#     uuid_pattern = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
#     lines = output.splitlines()
#     for i, line in enumerate(lines):
#         if line.strip().startswith("id"):
#             # 다음 줄이 값 라인
#             if i + 1 < len(lines):
#                 candidate = lines[i + 1].strip().split()[0]
#                 if uuid_pattern.match(candidate):
#                     return candidate
#     # 혹시라도 남아있을 수 있는 id 패턴
#     match = re.search(r"id\s+([a-f0-9-]{36})", output)
#     if match:
#         return match.group(1)
#     return None

# def wait_for_model_exists(model_id, timeout=5):
#     for _ in range(timeout):
#         get_result = run_cli_command(["model", "get", model_id])
#         if get_result.returncode == 0:
#             return True
#         time.sleep(1)
#     return False

# @pytest.mark.order(1)
# def test_cli_model_e2e():
#     # 1. Provider 생성
#     provider_name = generate_random_name("sdk_cli_test_provider")
#     result = run_cli_command([
#         "model", "provider", "create",
#         "--name", provider_name,
#         "--description", provider_name,
#         "--logo", provider_name
#     ])
#     assert result.returncode == 0
#     provider_id = extract_id_from_output(result.stdout)
#     assert provider_id is not None

#     try:
#         # 2. Serverless 모델 생성
#         model_name = generate_random_name("sdk_cli_serverless_model")
#         model_data = {
#             "display_name": model_name,
#             "name": model_name,
#             "type": "language",
#             "description": model_name + " description",
#             "serving_type": "serverless",
#             "provider_id": provider_id,
#             "languages": [{"name": "Korean"}],
#             "tasks": [{"name": "completion"}],
#             "tags": [{"name": "tag"}],
#             "policy": [{
#                 "decision_strategy": "UNANIMOUS",
#                 "logic": "POSITIVE",
#                 "policies": [{"logic": "POSITIVE", "names": ["admin"], "type": "user"}],
#                 "scopes": ["GET", "POST", "PUT", "DELETE"]
#             }],
#             "endpoint_url": "https://api.sktaip.com/v1",
#             "endpoint_identifier": "openai/gpt-3.5-turbo",
#             "endpoint_key": "key-1234567890"
#         }
#         with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
#             json.dump(model_data, f)
#             f.flush()
#             model_json_path = f.name
#         result = run_cli_command(["model", "create", "--json", model_json_path])
#         os.remove(model_json_path)
#         assert result.returncode == 0
#         model_id = extract_id_from_output(result.stdout)
#         assert model_id is not None

#         # 모델이 실제로 존재하는지 확인 (최대 5초 대기)
#         assert wait_for_model_exists(model_id), "Model not found after creation"

#         # 3. 모델 수정
#         model_data["description"] = model_name + " description updated"
#         with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
#             json.dump(model_data, f)
#             f.flush()
#             model_json_path = f.name
#         result = run_cli_command(["model", "update", "--json", model_json_path, model_id])
#         os.remove(model_json_path)
#         assert result.returncode == 0

#         # 4. 모델 목록
#         result = run_cli_command(["model", "list"])
#         assert result.returncode == 0
#         assert model_id in result.stdout

#         # 5. 모델 단건
#         result = run_cli_command(["model", "get", model_id])
#         assert result.returncode == 0
#         assert model_id in result.stdout

#         # 6. 태그 추가/삭제
#         result = run_cli_command(["model", "tag-add", model_id, "tag1", "tag2"])
#         assert result.returncode == 0
#         result = run_cli_command(["model", "tag-remove", model_id, "tag1"])
#         assert result.returncode == 0

#         # 7. 언어 추가/삭제
#         result = run_cli_command(["model", "lang-add", model_id, "English", "Japanese"])
#         assert result.returncode == 0
#         result = run_cli_command(["model", "lang-remove", model_id, "English"])
#         assert result.returncode == 0

#         # 8. 태스크 추가/삭제
#         result = run_cli_command(["model", "task-add", model_id, "translation", "summarization"])
#         assert result.returncode == 0
#         result = run_cli_command(["model", "task-remove", model_id, "translation"])
#         assert result.returncode == 0

#         # 9. 엔드포인트 등록
#         endpoint_data = {
#             "url": "https://api.example.com/v1/models/" + model_name,
#             "identifier": model_name,
#             "key": model_name,
#             "description": model_name + " endpoint"
#         }
#         result = run_cli_command([
#             "model", "endpoint", "create", model_id,
#             "--url", endpoint_data["url"],
#             "--identifier", endpoint_data["identifier"],
#             "--key", endpoint_data["key"],
#             "--description", endpoint_data["description"]
#         ])
#         assert result.returncode == 0
#         endpoint_id = extract_id_from_output(result.stdout)
#         assert endpoint_id is not None

#         # 10. 엔드포인트 목록
#         result = run_cli_command(["model", "endpoint", "list", model_id])
#         assert result.returncode == 0
#         assert endpoint_id in result.stdout

#         # 11. 엔드포인트 단건
#         result = run_cli_command(["model", "endpoint", "get", model_id, endpoint_id])
#         assert result.returncode == 0
#         assert endpoint_id in result.stdout

#         # 12. 엔드포인트 삭제
#         result = run_cli_command(["model", "endpoint", "delete", model_id, endpoint_id])
#         assert result.returncode == 0

#         # 13. 모델 삭제/복구/재삭제
#         result = run_cli_command(["model", "delete", model_id])
#         assert result.returncode == 0
#         time.sleep(1)
#         result = run_cli_command(["model", "recover", model_id])
#         assert result.returncode == 0
#         result = run_cli_command(["model", "delete", model_id])
#         assert result.returncode == 0
#         time.sleep(1)
#     finally:
#         try:
#             run_cli_command(["model", "provider", "delete", provider_id])
#         except Exception:
#             pass

# @pytest.mark.order(2)
# def test_cli_selfhosting_custom_model_e2e():
#     # 1. Provider 생성
#     provider_name = generate_random_name("sdk_cli_test_provider")
#     result = run_cli_command([
#         "model", "provider", "create",
#         "--name", provider_name,
#         "--description", provider_name,
#         "--logo", provider_name
#     ])
#     assert result.returncode == 0
#     provider_id = extract_id_from_output(result.stdout)
#     assert provider_id is not None

#     # 2. 모델/코드 파일 업로드
#     with tempfile.NamedTemporaryFile(suffix=".zip", dir="/tmp", delete=False) as tmp:
#         model_zip_path = tmp.name
#     with zipfile.ZipFile(model_zip_path, 'w') as zipf:
#         zipf.writestr("dummy.txt", "hello zip content")
#     result = run_cli_command(["model", "upload", model_zip_path])
#     os.remove(model_zip_path)
#     assert result.returncode == 0
#     model_path = None
#     try:
#         output_dict = ast.literal_eval(result.stdout.splitlines()[-1])
#         model_path = output_dict.get("temp_file_path")
#     except Exception:
#         match = re.search(r'"temp_file_path"\s*:\s*"([^"]+)"', result.stdout)
#         if match:
#             model_path = match.group(1)
#     time.sleep(2)
#     assert model_path is not None

#     with tempfile.NamedTemporaryFile(suffix=".zip", dir="/tmp", delete=False) as tmp:
#         code_zip_path = tmp.name
#     with zipfile.ZipFile(code_zip_path, 'w') as zipf:
#         zipf.writestr("dummy_code.py", "print('hello')")
#     result = run_cli_command(["model", "custom-runtime", "upload-code", "--file-path", code_zip_path])
#     os.remove(code_zip_path)
#     assert result.returncode == 0
#     custom_code_path = None
#     try:
#         output_dict = ast.literal_eval(result.stdout.splitlines()[-1])
#         custom_code_path = output_dict.get("temp_file_path")
#     except Exception:
#         match = re.search(r'"temp_file_path"\s*:\s*"([^"]+)"', result.stdout)
#         if match:
#             custom_code_path = match.group(1)
#     time.sleep(2)
#     assert custom_code_path is not None

#     try:
#         # 3. self-hosting + custom 모델 생성
#         model_name = generate_random_name("sdk_cli_selfhosting_model")
#         model_data = {
#             "display_name": model_name,
#             "name": model_name,
#             "type": "language",
#             "description": model_name + " description",
#             "serving_type": "self-hosting",
#             "is_private": False,
#             "provider_id": provider_id,
#             "is_custom": True,
#             "path": model_path,
#             "custom_code_path": custom_code_path,
#             "languages": [{"name": "English"}],
#             "tasks": [{"name": "completion"}],
#             "tags": [{"name": "tag1"}],
#             "policy": [{
#                 "decision_strategy": "UNANIMOUS",
#                 "logic": "POSITIVE",
#                 "policies": [{"logic": "POSITIVE", "names": ["admin"], "type": "user"}],
#                 "scopes": ["GET", "POST", "PUT", "DELETE"]
#             }]
#         }
#         with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
#             json.dump(model_data, f)
#             f.flush()
#             model_json_path = f.name
#         result = run_cli_command(["model", "create", "--json", model_json_path])
#         os.remove(model_json_path)
#         assert result.returncode == 0
#         model_id = extract_id_from_output(result.stdout)
#         assert model_id is not None

#         # 4. 커스텀 런타임 생성
#         result = run_cli_command([
#             "model", "custom-runtime", "create",
#             "--model-id", model_id,
#             "--image-url", "https://hub.docker.com/r/adxp/adxp-runtime-python/tags"
#         ])
#         assert result.returncode == 0

#         # 5. 커스텀 런타임 조회
#         result = run_cli_command(["model", "custom-runtime", "get", "--model-id", model_id])
#         assert result.returncode == 0

#         # 6. 커스텀 런타임 삭제
#         result = run_cli_command(["model", "custom-runtime", "delete", "--model-id", model_id])
#         assert result.returncode == 0

#         # 7. 모델 삭제
#         result = run_cli_command(["model", "delete", model_id])
#         assert result.returncode == 0

#     finally:
#         run_cli_command(["model", "provider", "delete", provider_id]) 

# def test_cli_provider_crud():
#     # create
#     name = generate_random_name("sdk_cli_test_provider_crud")
#     desc = name
#     logo = name
#     result = run_cli_command([
#         "model", "provider", "create",
#         "--name", name,
#         "--description", desc,
#         "--logo", logo
#     ])
#     assert result.returncode == 0
#     provider_id = extract_id_from_output(result.stdout)
#     assert provider_id is not None
#     # get
#     result = run_cli_command(["model", "provider", "get", provider_id])
#     assert result.returncode == 0
#     assert provider_id in result.stdout
#     # list
#     result = run_cli_command(["model", "provider", "list"])
#     assert result.returncode == 0
#     assert provider_id in result.stdout
#     # update
#     new_name = name + "_updated"
#     result = run_cli_command([
#         "model", "provider", "update", "--name", new_name, "--description", new_name, "--logo", new_name, provider_id
#     ])
#     assert result.returncode == 0
#     # delete
#     result = run_cli_command(["model", "provider", "delete", provider_id])
#     assert result.returncode == 0


# def test_cli_model_list_and_get_json():
#     # provider 생성
#     provider_name = generate_random_name("sdk_cli_test_provider_json")
#     result = run_cli_command([
#         "model", "provider", "create",
#         "--name", provider_name,
#         "--description", provider_name,
#         "--logo", provider_name
#     ])
#     assert result.returncode == 0
#     provider_id = extract_id_from_output(result.stdout)
#     assert provider_id is not None
#     try:
#         # 모델 생성
#         model_name = generate_random_name("sdk_cli_model_json")
#         model_data = {
#             "display_name": model_name,
#             "name": model_name,
#             "type": "language",
#             "description": model_name + " description",
#             "serving_type": "serverless",
#             "provider_id": provider_id,
#             "languages": [{"name": "Korean"}],
#             "tasks": [{"name": "completion"}],
#             "tags": [{"name": "tag"}],
#             "endpoint_url": "https://api.sktaip.com/v1",
#             "endpoint_identifier": "openai/gpt-3.5-turbo",
#             "endpoint_key": "key-1234567890"
#         }
#         with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
#             json.dump(model_data, f)
#             f.flush()
#             model_json_path = f.name
#         result = run_cli_command(["model", "create", "--json", model_json_path])
#         os.remove(model_json_path)
#         assert result.returncode == 0
#         model_id = extract_id_from_output(result.stdout)
#         assert model_id is not None
#         # model list --json
#         result = run_cli_command(["model", "list", "--json"])
#         assert result.returncode == 0
#         data = json.loads(result.stdout)
#         assert "data" in data
#         # model get --json
#         result = run_cli_command(["model", "get", model_id, "--json"])
#         assert result.returncode == 0
#         data = json.loads(result.stdout)
#         assert "id" in data
#     finally:
#         run_cli_command(["model", "provider", "delete", provider_id])


# def test_cli_model_update_display_name():
#     # provider 생성
#     provider_name = generate_random_name("sdk_cli_test_provider_update")
#     result = run_cli_command([
#         "model", "provider", "create",
#         "--name", provider_name,
#         "--description", provider_name,
#         "--logo", provider_name
#     ])
#     assert result.returncode == 0
#     provider_id = extract_id_from_output(result.stdout)
#     assert provider_id is not None
#     try:
#         # 모델 생성
#         model_name = generate_random_name("sdk_cli_model_update")
#         model_data = {
#             "display_name": model_name,
#             "name": model_name,
#             "type": "language",
#             "description": model_name + " description",
#             "serving_type": "serverless",
#             "provider_id": provider_id,
#             "languages": [{"name": "Korean"}],
#             "tasks": [{"name": "completion"}],
#             "tags": [{"name": "tag"}],
#             "endpoint_url": "https://api.sktaip.com/v1",
#             "endpoint_identifier": "openai/gpt-3.5-turbo",
#             "endpoint_key": "key-1234567890"
#         }
#         with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
#             json.dump(model_data, f)
#             f.flush()
#             model_json_path = f.name
#         result = run_cli_command(["model", "create", "--json", model_json_path])
#         os.remove(model_json_path)
#         assert result.returncode == 0
#         model_id = extract_id_from_output(result.stdout)
#         assert model_id is not None
#         # display_name 변경
#         new_display_name = model_name + "_updated"
#         result = run_cli_command([
#             "model", "update", "--display-name", new_display_name, model_id
#         ])
#         assert result.returncode == 0
#         # get으로 변경 확인
#         result = run_cli_command(["model", "get", model_id])
#         assert result.returncode == 0
#         assert new_display_name in result.stdout
#     finally:
#         run_cli_command(["model", "provider", "delete", provider_id])


# def test_cli_tag_lang_task_endpoint_customruntime_json():
#     # provider 생성
#     provider_name = generate_random_name("sdk_cli_test_provider_json2")
#     result = run_cli_command([
#         "model", "provider", "create",
#         "--name", provider_name,
#         "--description", provider_name,
#         "--logo", provider_name
#     ])
#     assert result.returncode == 0
#     provider_id = extract_id_from_output(result.stdout)
#     assert provider_id is not None
#     try:
#         # 모델 생성
#         model_name = generate_random_name("sdk_cli_model_json2")
#         model_data = {
#             "display_name": model_name,
#             "name": model_name,
#             "type": "language",
#             "description": model_name + " description",
#             "serving_type": "serverless",
#             "provider_id": provider_id,
#             "languages": [{"name": "Korean"}],
#             "tasks": [{"name": "completion"}],
#             "tags": [{"name": "tag"}],
#             "endpoint_url": "https://api.sktaip.com/v1",
#             "endpoint_identifier": "openai/gpt-3.5-turbo",
#             "endpoint_key": "key-1234567890"
#         }
#         with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
#             json.dump(model_data, f)
#             f.flush()
#             model_json_path = f.name
#         result = run_cli_command(["model", "create", "--json", model_json_path])
#         os.remove(model_json_path)
#         assert result.returncode == 0
#         model_id = extract_id_from_output(result.stdout)
#         assert model_id is not None
#         # tag-add --json
#         result = run_cli_command(["model", "tag-add", model_id, "tag1", "tag2", "--json"])
#         assert result.returncode == 0
#         data = json.loads(result.stdout)
#         assert "tags" in data
#         # lang-add --json
#         result = run_cli_command(["model", "lang-add", model_id, "English", "Japanese", "--json"])
#         assert result.returncode == 0
#         data = json.loads(result.stdout)
#         assert "languages" in data
#         # task-add --json
#         result = run_cli_command(["model", "task-add", model_id, "translation", "summarization", "--json"])
#         assert result.returncode == 0
#         data = json.loads(result.stdout)
#         assert "tasks" in data
#         # endpoint list --json
#         result = run_cli_command(["model", "endpoint", "list", model_id, "--json"])
#         assert result.returncode == 0
#         data = json.loads(result.stdout)
#         assert "data" in data
#         # custom-runtime get --json
#         result = run_cli_command(["model", "custom-runtime", "get", "--model-id", model_id, "--json"])
#         # custom-runtime이 없을 수도 있으니 에러가 나도 무시
#     finally:
#         run_cli_command(["model", "provider", "delete", provider_id]) 