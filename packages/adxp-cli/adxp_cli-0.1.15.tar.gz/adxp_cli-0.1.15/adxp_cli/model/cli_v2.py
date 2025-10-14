"""
Model CLI V2

Click 기반의 명령줄 인터페이스입니다.
핵심 CRUD 기능만 제공합니다.
"""

import click
import json
import os
from typing import Optional, List
from tabulate import tabulate

try:
    from adxp_sdk.models import AXModelHubV2, ModelType, ServingType
except ImportError:
    from adxp_sdk.models.hub_v2 import AXModelHubV2
    from adxp_sdk.models.schemas_v2 import ModelType, ServingType


@click.group()
@click.option('--base-url', default='https://aip-stg.sktai.io', help='API 기본 URL')
@click.option('--api-key', envvar='MODEL_API_KEY', help='API 키')
@click.pass_context
def cli_v2(ctx, base_url: str, api_key: str):
    """Model CRUD CLI V2 - 핵심 CRUD 기능만 제공"""
    if not api_key:
        click.echo("Error: API 키가 필요합니다. --api-key 옵션 또는 MODEL_API_KEY 환경변수를 설정하세요.", err=True)
        ctx.exit(1)
    
    ctx.ensure_object(dict)
    ctx.obj['client'] = AXModelHubV2(base_url=base_url, api_key=api_key)


@cli_v2.command()
@click.option('--name', required=True, help='모델 이름')
@click.option('--type', 'model_type', required=True, type=click.Choice([t.value for t in ModelType]), help='모델 타입')
@click.option('--provider-id', required=True, help='프로바이더 ID')
@click.option('--serving-type', required=True, type=click.Choice([t.value for t in ServingType]), help='서빙 타입')
@click.option('--display-name', help='표시 이름')
@click.option('--description', help='모델 설명')
@click.option('--size', help='모델 크기')
@click.option('--token-size', help='토큰 크기')
@click.option('--license', help='라이선스')
@click.option('--readme', help='README 내용')
@click.option('--tags', help='태그 (JSON 배열 형태)')
@click.option('--languages', help='언어 (JSON 배열 형태)')
@click.option('--tasks', help='태스크 (JSON 배열 형태)')
@click.option('--is-private', is_flag=True, help='비공개 모델')
@click.option('--is-custom', is_flag=True, help='커스텀 모델')
# Serverless 옵션
@click.option('--endpoint-url', help='엔드포인트 URL (serverless)')
@click.option('--endpoint-identifier', help='엔드포인트 식별자 (serverless)')
@click.option('--endpoint-key', help='엔드포인트 키 (serverless)')
@click.option('--endpoint-description', help='엔드포인트 설명 (serverless)')
# Self-hosting 옵션
@click.option('--path', help='모델 파일 경로 (self-hosting)')
@click.option('--file', help='업로드할 모델 파일 (self-hosting)')
@click.option('--dtype', help='데이터 타입 (self-hosting)')
@click.option('--quantization', help='양자화 설정 (JSON 객체)')
@click.option('--custom-runtime', help='커스텀 런타임 설정 (JSON 객체)')
@click.option('--endpoints', help='엔드포인트 설정 (JSON 객체)')
# Custom 옵션
@click.option('--custom-code-path', help='커스텀 코드 경로')
@click.option('--custom-code-file', help='업로드할 커스텀 코드 파일')
@click.option('--custom-runtime-image-url', help='커스텀 런타임 이미지 URL')
@click.option('--custom-runtime-use-bash', is_flag=True, help='커스텀 런타임 bash 사용')
@click.option('--custom-runtime-command', help='커스텀 런타임 명령어 (JSON 배열)')
@click.option('--custom-runtime-args', help='커스텀 런타임 인자 (JSON 배열)')
@click.pass_context
def create(ctx, **kwargs):
    """모델 생성"""
    client = ctx.obj['client']
    
    # Self-hosting 모델의 경우 파일 업로드 후 path는 API가 자동으로 모델 ID와 동일한 UUID로 설정
    if kwargs.get('serving_type') == 'self-hosting' and kwargs.get('file'):
        if not os.path.exists(kwargs['file']):
            click.echo(f"Error: 파일을 찾을 수 없습니다: {kwargs['file']}", err=True)
            ctx.exit(1)
        
        try:
            click.echo(f"파일 업로드 중: {kwargs['file']}")
            upload_result = client.upload_model_file(kwargs['file'])
            click.echo(f"파일 업로드 완료: {upload_result.get('file_name')}")
            click.echo("path 필드는 API가 자동으로 모델 ID와 동일한 UUID로 설정합니다.")
        except Exception as e:
            click.echo(f"Error: 파일 업로드 실패: {e}", err=True)
            ctx.exit(1)
        
        # file 옵션을 제거 (path에 사용하지 않음)
        kwargs.pop('file', None)
    
    # Custom Self-hosting 모델의 경우 커스텀 코드 파일 업로드
    if kwargs.get('is_custom') and kwargs.get('custom_code_file'):
        if not os.path.exists(kwargs['custom_code_file']):
            click.echo(f"Error: 커스텀 코드 파일을 찾을 수 없습니다: {kwargs['custom_code_file']}", err=True)
            ctx.exit(1)
        
        try:
            click.echo(f"커스텀 코드 파일 업로드 중: {kwargs['custom_code_file']}")
            custom_upload_result = client.upload_model_file(kwargs['custom_code_file'])
            click.echo(f"커스텀 코드 파일 업로드 완료: {custom_upload_result.get('file_name')}")
            kwargs['custom_code_path'] = custom_upload_result.get('temp_file_path')
        except Exception as e:
            click.echo(f"Error: 커스텀 코드 파일 업로드 실패: {e}", err=True)
            ctx.exit(1)
        
        # custom_code_file 옵션을 제거
        kwargs.pop('custom_code_file', None)
    
    # JSON 파싱
    for field in ['tags', 'languages', 'tasks', 'custom_runtime_command', 'custom_runtime_args', 'quantization', 'custom_runtime', 'endpoints']:
        if kwargs.get(field):
            try:
                kwargs[field] = json.loads(kwargs[field])
            except json.JSONDecodeError:
                click.echo(f"Error: {field}는 유효한 JSON이어야 합니다.", err=True)
                ctx.exit(1)
    
    # None 값 제거
    model_data = {k: v for k, v in kwargs.items() if v is not None}
    
    try:
        result = client.create_model(model_data)
        click.echo("모델이 성공적으로 생성되었습니다:")
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.option('--page', default=1, help='페이지 번호')
@click.option('--size', default=10, help='페이지 크기')
@click.option('--type', 'model_type', help='모델 타입 필터')
@click.option('--serving-type', help='서빙 타입 필터')
@click.option('--provider-id', help='프로바이더 ID 필터')
@click.option('--tags', help='태그 필터 (쉼표로 구분)')
@click.option('--languages', help='언어 필터 (쉼표로 구분)')
@click.option('--tasks', help='태스크 필터 (쉼표로 구분)')
@click.option('--is-private', is_flag=True, help='비공개 모델 필터')
@click.option('--is-custom', is_flag=True, help='커스텀 모델 필터')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='출력 형식')
@click.pass_context
def list_models(ctx, **kwargs):
    """모델 목록 조회"""
    client = ctx.obj['client']
    
    # 필터 파라미터 처리
    filters = {}
    for key, value in kwargs.items():
        if key in ['page', 'size', 'serving_type', 'provider_id', 'is_private', 'is_custom'] and value is not None:
            filters[key] = value
        elif key == 'model_type' and value is not None:
            filters['type'] = value  # model_type을 type으로 변환
        elif key in ['tags', 'languages', 'tasks'] and value:
            filters[key] = value.split(',')
    
    try:
        result = client.get_models(**filters)
        
        if kwargs['output_format'] == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            models = result.get('data', [])
            if not models:
                click.echo("모델이 없습니다.")
                return
            
            # 테이블 헤더
            headers = ['ID', 'Name', 'Type', 'Serving Type', 'Provider', 'Created At']
            rows = []
            
            for model in models:
                rows.append([
                    model.get('id', '')[:8] + '...',
                    model.get('name', ''),
                    model.get('type', ''),
                    model.get('serving_type', ''),
                    model.get('provider_id', '')[:8] + '...' if model.get('provider_id') else '',
                    model.get('created_at', '')[:10] if model.get('created_at') else ''
                ])
            
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.argument('model_id')
@click.pass_context
def get(ctx, model_id: str):
    """특정 모델 조회"""
    client = ctx.obj['client']
    
    try:
        result = client.get_model(model_id)
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.argument('model_id')
@click.option('--display-name', help='표시 이름')
@click.option('--description', help='모델 설명')
@click.option('--size', help='모델 크기')
@click.option('--token-size', help='토큰 크기')
@click.option('--license', help='라이선스')
@click.option('--readme', help='README 내용')
@click.option('--tags', help='태그 (JSON 배열 형태)')
@click.option('--languages', help='언어 (JSON 배열 형태)')
@click.option('--tasks', help='태스크 (JSON 배열 형태)')
@click.option('--is-private', type=bool, help='비공개 모델 여부')
@click.pass_context
def update(ctx, model_id: str, **kwargs):
    """모델 업데이트 (모든 필드를 한 번에 업데이트)"""
    client = ctx.obj['client']
    
    # JSON 파싱
    for field in ['languages', 'tasks']:
        if kwargs.get(field):
            try:
                kwargs[field] = json.loads(kwargs[field])
            except json.JSONDecodeError:
                click.echo(f"Error: {field}는 유효한 JSON 배열이어야 합니다.", err=True)
                ctx.exit(1)
    
    # None 값 제거
    update_data = {k: v for k, v in kwargs.items() if v is not None}
    
    if not update_data:
        click.echo("업데이트할 데이터가 없습니다.")
        return
    
    try:
        result = client.update_model(model_id, update_data)
        click.echo("모델이 성공적으로 업데이트되었습니다:")
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.argument('model_id')
@click.confirmation_option(prompt='정말로 이 모델을 삭제하시겠습니까?')
@click.pass_context
def delete(ctx, model_id: str):
    """모델 삭제"""
    client = ctx.obj['client']
    
    try:
        result = client.delete_model(model_id)
        click.echo("모델이 성공적으로 삭제되었습니다:")
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.argument('model_id')
@click.option('--tags', required=True, help='추가할 태그 (JSON 배열 형태)')
@click.pass_context
def add_tags(ctx, model_id, tags):
    """모델에 태그 추가"""
    client = ctx.obj['client']
    
    try:
        tags_data = json.loads(tags)
        result = client.add_tags_to_model(model_id, tags_data)
        click.echo("✅ 태그 추가 성공!")
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        click.echo("Error: tags 필드의 JSON 형식이 올바르지 않습니다.", err=True)
        ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: 태그 추가 실패: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.argument('model_id')
@click.option('--tags', required=True, help='제거할 태그 (JSON 배열 형태)')
@click.pass_context
def remove_tags(ctx, model_id, tags):
    """모델에서 태그 제거"""
    client = ctx.obj['client']
    
    try:
        tags_data = json.loads(tags)
        result = client.remove_tags_from_model(model_id, tags_data)
        click.echo("✅ 태그 제거 성공!")
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        click.echo("Error: tags 필드의 JSON 형식이 올바르지 않습니다.", err=True)
        ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: 태그 제거 실패: {e}", err=True)
        ctx.exit(1)


if __name__ == '__main__':
    cli_v2()
