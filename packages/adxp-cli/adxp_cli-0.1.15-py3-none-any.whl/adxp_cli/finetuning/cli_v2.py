"""
Finetuning CLI V2

Click 기반의 명령줄 인터페이스입니다.
핵심 CRUD 기능만 제공합니다.
"""

import click
import json
import os
from typing import Optional, List
from tabulate import tabulate

try:
    from adxp_sdk.finetuning.hub_v2 import AXFinetuningHubV2
    from adxp_sdk.finetuning.schemas_v2 import FinetuningStatus
except ImportError:
    # 직접 실행할 때를 위한 절대 import
    from hub_v2 import AXFinetuningHubV2
    from schemas_v2 import FinetuningStatus


@click.group()
@click.pass_context
def cli_v2(ctx):
    """Finetuning CRUD CLI V2 - 핵심 CRUD 기능만 제공"""
    try:
        # CLI의 저장된 인증 정보 사용
        from adxp_cli.auth.service import get_credential
        headers, config = get_credential()
        
        if not config.token:
            click.echo("Error: 저장된 인증 정보가 없습니다. 'adxp-cli auth login' 명령어로 로그인하세요.", err=True)
            ctx.exit(1)
        
        ctx.ensure_object(dict)
        ctx.obj['client'] = AXFinetuningHubV2(config.base_url, config.token)
        
    except Exception as e:
        click.echo(f"Error: 인증 정보를 가져올 수 없습니다: {e}", err=True)
        click.echo("'adxp-cli auth login' 명령어로 로그인하세요.", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.option('--name', required=True, help='트레이닝 이름')
@click.option('--project_id', required=True, help='프로젝트 ID')
@click.option('--task_id', required=True, help='태스크 ID')
@click.option('--trainer_id', required=True, help='트레이너 ID')
@click.option('--dataset_ids', required=True, help='데이터셋 ID 목록 (JSON 배열 형태)')
@click.option('--base_model_id', required=True, help='베이스 모델 ID')
@click.option('--resource', required=True, help='리소스 설정 (JSON 객체 형태)')
@click.option('--params', required=True, help='트레이닝 파라미터 (문자열)')
@click.option('--description', help='트레이닝 설명')
@click.option('--id', help='트레이닝 ID (UUID, 자동 생성됨)')
@click.option('--envs', help='환경 변수 (JSON 객체 형태)')
@click.option('--is-auto-model-creation', is_flag=True, help='훈련 완료 후 자동 모델 생성')
@click.option('--policy', help='접근 정책 설정 (JSON 배열 형태)')
@click.option('--use-lora', type=bool, help='LoRA 사용 여부')
@click.option('--num-train-epochs', type=int, help='훈련 에포크 수')
@click.option('--validation-split', type=float, help='검증 데이터 분할 비율')
@click.option('--learning-rate', type=float, help='학습률')
@click.option('--batch-size', type=int, help='배치 크기')
@click.option('--early-stopping', type=bool, help='얼리 스토핑 사용 여부')
@click.option('--early-stopping-patience', type=int, help='얼리 스토핑 인내심 (early-stopping이 True일 때만 유효)')
@click.pass_context
def create_training(ctx, **kwargs):
    """트레이닝 생성"""
    client = ctx.obj['client']
    
    # JSON 파싱
    for field in ['dataset_ids', 'resource', 'envs', 'policy']:
        if kwargs.get(field):
            try:
                kwargs[field] = json.loads(kwargs[field])
            except json.JSONDecodeError as e:
                click.echo(f"Error: {field} 필드의 JSON 형식이 올바르지 않습니다.", err=True)
                click.echo(f"받은 값: {repr(kwargs[field])}", err=True)
                ctx.exit(1)
    
    # training_config 구성
    training_config_fields = ['use_lora', 'num_train_epochs', 'validation_split', 'learning_rate', 'batch_size', 'early_stopping', 'early_stopping_patience']
    training_config = {}
    for field in training_config_fields:
        if kwargs.get(field) is not None:
            training_config[field] = kwargs[field]
    
    # early_stopping이 False일 때 early_stopping_patience를 None으로 설정
    if training_config.get('early_stopping') is False:
        training_config['early_stopping_patience'] = None
    
    if training_config:
        kwargs['training_config'] = training_config
    
    # None 값 제거
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    
    try:
        result = client.create_training(kwargs)
        click.echo("✅ 트레이닝 생성 성공!")
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: 트레이닝 생성 실패: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.option('--limit', type=int, help='조회할 개수')
@click.option('--offset', type=int, help='시작 위치')
@click.option('--status', help='상태 필터')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='출력 형식')
@click.pass_context
def list_trainings(ctx, limit, offset, status, output_format):
    """트레이닝 목록 조회"""
    client = ctx.obj['client']
    
    try:
        result = client.get_trainings(
            limit=limit,
            offset=offset,
            status=status
        )
        
        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # 테이블 형식으로 출력
            trainings = result.get('data', [])
            if not trainings:
                click.echo("트레이닝이 없습니다.")
                return
            
            headers = ['ID', 'Name', 'Status', 'Progress', 'Base Model', 'Created At']
            rows = []
            for training in trainings:
                progress = training.get('progress', {})
                progress_text = f"{progress.get('percentage', 0):.1f}%" if progress.get('percentage') else "N/A"
                
                rows.append([
                    training.get('id', 'N/A')[:8] + '...',
                    training.get('name', 'N/A'),
                    training.get('status', 'N/A'),
                    progress_text,
                    training.get('base_model_id', 'N/A')[:8] + '...' if training.get('base_model_id') else 'N/A',
                    training.get('created_at', 'N/A')[:19] if training.get('created_at') else 'N/A'
                ])
            
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.argument('training_id')
@click.pass_context
def get_training(ctx, training_id):
    """특정 트레이닝 조회"""
    client = ctx.obj['client']
    
    try:
        result = client.get_training_by_id(training_id)
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.argument('training_id')
@click.option('--name', help='트레이닝 이름')
@click.option('--description', help='트레이닝 설명')
@click.option('--params', help='트레이닝 파라미터 (문자열)')
@click.option('--envs', help='환경 변수 (JSON 객체 형태)')
@click.option('--resource', help='리소스 설정 (JSON 객체 형태)')
@click.option('--id', help='트레이닝 ID (UUID)')
@click.option('--is-auto-model-creation', is_flag=True, help='훈련 완료 후 자동 모델 생성')
@click.option('--policy', help='접근 정책 설정 (JSON 배열 형태)')
@click.pass_context
def update_training(ctx, training_id: str, **kwargs):
    """트레이닝 업데이트"""
    client = ctx.obj['client']
    
    # JSON 파싱
    for field in ['envs', 'resource', 'policy']:
        if kwargs.get(field):
            try:
                kwargs[field] = json.loads(kwargs[field])
            except json.JSONDecodeError:
                click.echo(f"Error: {field}는 유효한 JSON 객체여야 합니다.", err=True)
                ctx.exit(1)
    
    # None 값 제거
    update_data = {k: v for k, v in kwargs.items() if v is not None}
    
    if not update_data:
        click.echo("Error: 업데이트할 필드가 없습니다.", err=True)
        ctx.exit(1)
    
    try:
        result = client.update_training(training_id, update_data)
        click.echo("트레이닝이 성공적으로 업데이트되었습니다:")
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.argument('training_id')
@click.confirmation_option(prompt='정말로 이 트레이닝을 취소하시겠습니까?')
@click.pass_context
def cancel_training(ctx, training_id: str):
    """트레이닝 취소"""
    client = ctx.obj['client']
    
    try:
        result = client.cancel_training(training_id)
        click.echo("트레이닝이 성공적으로 취소되었습니다.")
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.argument('training_id')
@click.pass_context
def delete_training(ctx, training_id: str):
    """트레이닝 삭제"""
    client = ctx.obj['client']
    
    try:
        result = client.delete_training(training_id)
        click.echo("트레이닝이 성공적으로 삭제되었습니다.")
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.argument('training_id')
@click.option('--after', help='특정 시간 이후의 이벤트 필터링 (ISO 8601 형식, 예: 2024-10-22T15:00:00.000Z)')
@click.option('--limit', default=100, help='반환될 이벤트의 최대 개수 (기본값: 100)')
@click.pass_context
def get_logs(ctx, training_id: str, after: str, limit: int):
    """트레이닝 이벤트/로그 조회"""
    client = ctx.obj['client']
    
    try:
        result = client.get_training_logs(training_id, after=after, limit=limit)
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.argument('training_id')
@click.pass_context
def get_metrics(ctx, training_id: str):
    """트레이닝 메트릭 조회"""
    client = ctx.obj['client']
    
    try:
        result = client.get_training_metrics(training_id)
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.argument('training_id')
@click.pass_context
def start_training(ctx, training_id):
    """트레이닝 시작"""
    client = ctx.obj['client']
    
    try:
        # 트레이닝 시작 - status를 'starting'으로 업데이트
        update_data = {'status': 'starting'}
        result = client.update_training(training_id, update_data)
        click.echo("✅ 트레이닝 시작 요청 성공!")
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: 트레이닝 시작 실패: {e}", err=True)
        ctx.exit(1)


@cli_v2.command()
@click.argument('training_id')
@click.pass_context
def stop_training(ctx, training_id):
    """트레이닝 중지"""
    client = ctx.obj['client']
    
    try:
        # 트레이닝 중지 - status를 'stopping'으로 업데이트
        update_data = {'status': 'stopping'}
        result = client.update_training(training_id, update_data)
        click.echo("✅ 트레이닝 중지 요청 성공!")
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: 트레이닝 중지 실패: {e}", err=True)
        ctx.exit(1)


if __name__ == '__main__':
    cli_v2()
