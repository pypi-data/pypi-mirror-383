## 지원하는 모델 타입

### 1. Self-hosting 모델
- `serving_type`이 `'self-hosting'`인 경우
- 로컬 모델 파일을 자동으로 업로드
- `path` 필드에 로컬 파일 경로 지정 필요

### 2. Serverless 모델
- `serving_type`이 `'serverless'`인 경우
- 외부 API 엔드포인트 정보 필요
- 엔드포인트 자동 생성 지원

### 3. Custom 모델
- `is_custom=True`인 경우
- 커스텀 런타임 설정 필요
- 커스텀 코드 파일 자동 업로드

## 기능

### 1. 자동 파일 업로드
- **Self-hosting 모델**: `path`에 로컬 파일 경로가 지정된 경우 자동으로 `upload_model_file()`을 호출하여 파일을 업로드
- **Custom 모델**: `custom_code_path`에 로컬 파일 경로가 지정된 경우 자동으로 `upload_custom_code_file()`을 호출하여 파일을 업로드
- 응답의 `temp_file_path`를 해당 필드에 설정
- 최종적으로 `create_model()`을 호출하여 모델 생성

### 2. 엔드포인트 자동 생성
- `serving_type`이 `'serverless'`이고 endpoint 관련 파라미터가 제공된 경우
- 모델 생성 후 자동으로 엔드포인트 생성
- `endpoint_url`, `endpoint_identifier`, `endpoint_key` 필수

### 3. 커스텀 런타임 자동 생성
- `is_custom=True`이고 `custom_runtime_image_url`이 제공된 경우
- 모델 생성 후 자동으로 커스텀 런타임 생성
- `custom_runtime_image_url` 필수

### 4. 통합된 인터페이스

#### SDK 사용법

**Parameter Style (권장)**
```python
from adxp_sdk.models.hub import AXModelHub

hub = AXModelHub(credentials)

# 기본 Self-hosting 모델
result = hub.create_model(
    name="my-model",
    type="language",
    serving_type="self-hosting",
    path="/path/to/model.bin"
)

# Serverless 모델 with Endpoint
result = hub.create_model(
    name="gpt-model",
    type="language",
    display_name="GPT-3.5",
    description="Large language model for text generation",
    size="175B",
    token_size="2048",
    serving_type="serverless",
    provider_id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    is_private=True,
    path="/path/to/gpt-model.bin",
    tags=["llm", "gpt", "text-generation"],
    languages=["ko", "en"],
    tasks=["completion", "chat"],
    inference_param={"temperature": 0.7, "max_tokens": 100},
    default_params={"model": "gpt-3.5-turbo"},
    endpoint_url="https://api.sktaip.com/v1",
    endpoint_identifier="openai/gpt-3.5-turbo",
    endpoint_key="key-1234567890"
)

# Custom 모델 with Custom Runtime
result = hub.create_model(
    name="custom-model",
    type="language",
    display_name="Custom Language Model",
    description="Custom model with custom runtime",
    serving_type="self-hosting",
    provider_id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    is_custom=True,
    path="/path/to/model.zip",
    custom_code_path="/path/to/custom-code.zip",
    custom_runtime_image_url="https://hub.docker.com/r/adxpai/adxp-custom-runtime",
    custom_runtime_use_bash=True,
    custom_runtime_command=["/bin/bash", "-c"],
    custom_runtime_args=["uvicorn", "main:app"]
)
```

**Dict Style (고급 사용자용)**
```python
# 기존 방식과 동일하게 dict로 전달
result = hub.create_model({
    "name": "my-model",
    "type": "language",
    "serving_type": "self-hosting",
    "path": "/path/to/model.bin"  # 자동으로 업로드됨
})
```

#### CLI 사용법

**Parameter Style (권장)**
```bash
# 기본 Self-hosting 모델
adxp-cli model create --name "my-model" --type "language" --serving-type "self-hosting" --path "/path/to/model.bin"

# Serverless 모델 with Endpoint
adxp-cli model create \
  --name "gpt-model" \
  --type "language" \
  --display-name "GPT-3.5" \
  --description "Large language model for text generation" \
  --size "175B" \
  --token-size "2048" \
  --serving-type "serverless" \
  --provider-id "3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  --is-private \
  --path "/path/to/gpt-model.bin" \
  --tags "llm" "gpt" "text-generation" \
  --languages "ko" "en" \
  --tasks "completion" "chat" \
  --inference-param '{"temperature": 0.7, "max_tokens": 100}' \
  --default-params '{"model": "gpt-3.5-turbo"}' \
  --endpoint-url "https://api.sktaip.com/v1" \
  --endpoint-identifier "openai/gpt-3.5-turbo" \
  --endpoint-key "key-1234567890"

# Custom 모델 with Custom Runtime
adxp-cli model create \
  --name "custom-model" \
  --type "language" \
  --display-name "Custom Language Model" \
  --description "Custom model with custom runtime" \
  --serving-type "self-hosting" \
  --provider-id "3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  --is-custom \
  --path "/path/to/model.zip" \
  --custom-code-path "/path/to/custom-code.zip" \
  --custom-runtime-image-url "https://hub.docker.com/r/adxpai/adxp-custom-runtime" \
  --custom-runtime-use-bash \
  --custom-runtime-command "/bin/bash,-c" \
  --custom-runtime-args "uvicorn,main:app"
```

**JSON File Style**
```bash
# JSON 파일로 모델 생성
adxp-cli model create --json model_config.json
```

## 지원되는 모든 필드

### 필수 필드
- `name` (str): 모델 이름
- `type` (str): 모델 타입 (`language`, `embedding`, `image`, `multimodal`, `reranker`, `stt`, `tts`, `audio`, `code`, `vision`, `video`)
- `provider_id` (str): 프로바이더 ID

### 조건부 필드
- `serving_type` (str): 서빙 타입 (`serverless`, `self-hosting`)
- `path` (str): 모델 파일 경로 (serving_type="self-hosting"일 때 필수)
- `endpoint_url` (str): 엔드포인트 URL (serving_type="serverless"일 때 필수)
- `endpoint_identifier` (str): 엔드포인트 식별자 (serving_type="serverless"일 때 필수)
- `endpoint_key` (str): 엔드포인트 키 (serving_type="serverless"일 때 필수)
- `custom_code_path` (str): 커스텀 코드 경로 (is_custom=True일 때 필수)
- `custom_runtime_image_url` (str): 커스텀 런타임 이미지 URL (is_custom=True일 때 필수)

### 선택 필드
- `display_name` (str): 표시 이름
- `description` (str): 모델 설명
- `size` (str): 모델 크기
- `token_size` (str): 토큰 크기
- `dtype` (str): 데이터 타입
- `is_private` (bool): 비공개 여부
- `is_valid` (bool): 유효성 여부
- `license` (str): 라이선스 정보
- `readme` (str): README 내용
- `project_id` (str): 프로젝트 ID
- `last_version` (int): 마지막 버전 번호
- `is_custom` (bool): 커스텀 모델 여부
- `custom_code_path` (str): 커스텀 코드 경로

### 커스텀 런타임 필드 (is_custom=True일 때)
- `custom_runtime_use_bash` (bool): Bash 사용 여부 (기본값: False)
- `custom_runtime_command` (List[str]): 실행 명령어
- `custom_runtime_args` (List[str]): 실행 인자

### JSON 파라미터 필드
- `inference_param` (Dict): 추론 파라미터
- `quantization` (Dict): 양자화 파라미터
- `default_params` (Dict): 기본 파라미터

### 리스트 필드
- `tags` (List[str]): 태그 목록
- `languages` (List[str]): 언어 목록
- `tasks` (List[str]): 작업 목록

## 사용 스타일 비교

### Parameter Style (권장)
**장점:**
- IDE 자동완성 지원
- 타입 안전성
- 명확한 파라미터 이름
- 학습하기 쉬움

**사용 시기:**
- 간단한 모델 생성
- 대부분의 사용자

### Dict Style (고급)
**장점:**
- 유연한 구조
- 복잡한 설정에 적합
- 기존 API와 동일한 방식

**사용 시기:**
- 복잡한 모델 설정
- 고급 사용자

## 자동화 기능

### 1. 파일 업로드 자동화
- **Self-hosting 모델**: `path` 필드의 로컬 파일을 자동으로 업로드
- **Custom 모델**: `custom_code_path` 필드의 로컬 파일을 자동으로 업로드
- 이미 `/tmp/`로 시작하는 경로는 업로드되지 않음 (이미 업로드된 파일로 간주)

### 2. 엔드포인트 자동 생성
- `serving_type="serverless"`이고 endpoint 관련 파라미터가 모두 제공된 경우
- 모델 생성 후 자동으로 엔드포인트 생성
- 생성된 엔드포인트 정보를 응답에 포함

### 3. 커스텀 런타임 자동 생성
- `is_custom=True`이고 `custom_runtime_image_url`이 제공된 경우
- 모델 생성 후 자동으로 커스텀 런타임 생성
- 생성된 커스텀 런타임 정보를 응답에 포함

## 주의사항

1. **Self-hosting 모델**: `serving_type`이 `'self-hosting'`인 경우 `path` 필드가 필수이며, 자동으로 파일 업로드가 수행됩니다.

2. **Serverless 모델**: `serving_type`이 `'serverless'`인 경우 `endpoint_url`, `endpoint_identifier`, `endpoint_key`가 필수입니다.

3. **Custom 모델**: `is_custom=True`인 경우 `custom_code_path`와 `custom_runtime_image_url`이 필수입니다.

4. **필수 필드**: 모든 모델에 대해 `name`, `type`, `provider_id`는 필수입니다.

5. **파일 경로**: 이미 `/tmp/`외의 경로로 시작하는 것을 권장합니다.

6. **JSON 파라미터**: CLI에서 JSON 파라미터를 사용할 때는 유효한 JSON 문자열을 입력해야 합니다.

7. **통합된 인터페이스**: 하나의 메서드로 두 가지 스타일을 모두 지원하여 사용자 선택의 자유를 제공합니다.

8. **응답 구조**: 
   - 일반 모델: 모델 정보만 반환
   - Serverless 모델: 모델 정보와 엔드포인트 정보 반환
   - Custom 모델: 모델 정보와 커스텀 런타임 정보 반환
   - Serverless + Custom 모델: 모델, 엔드포인트, 커스텀 런타임 정보 모두 반환 