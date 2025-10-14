"""
Dataset CRUD CLI

Click 기반의 명령줄 인터페이스입니다.
핵심 CRUD 기능만 제공합니다.
"""

import click
import json
import os
from typing import Dict, Any, Optional, List

try:
    from adxp_sdk.dataset.hub import AXDatasetHub
    from adxp_sdk.dataset.schemas import (
        DatasetCreateRequest, DatasetUpdateRequest, DatasetType,
        DatasetFile, DatasetTag, DatasetProcessor, DatasetFilter
    )
except ImportError:
    # 직접 실행할 때를 위한 절대 import
    from adxp_sdk.dataset.hub import AXDatasetHub
    from adxp_sdk.dataset.schemas import (
        DatasetCreateRequest, DatasetUpdateRequest, DatasetType,
        DatasetFile, DatasetTag, DatasetProcessor, DatasetFilter
    )


def print_json(data: Dict[str, Any], indent: int = 2) -> None:
    """JSON 데이터를 보기 좋게 출력"""
    click.echo(json.dumps(data, ensure_ascii=False, indent=indent))


@click.group()
@click.pass_context
def cli(ctx):
    """Dataset CRUD CLI - 핵심 CRUD 기능만 제공"""
    try:
        from ..auth.service import get_credential
        headers, config = get_credential()
        
        if not config.token:
            click.echo("Error: 저장된 인증 정보가 없습니다. 'adxp-cli auth login' 명령어로 로그인하세요.", err=True)
            ctx.exit(1)
        
        ctx.ensure_object(dict)
        # base_url에 /api/v1 추가
        dataset_base_url = f"{config.base_url}/api/v1"
        ctx.obj['client'] = AXDatasetHub(dataset_base_url, config.token)
        
    except Exception as e:
        click.echo(f"Error: 인증 정보를 가져올 수 없습니다: {e}", err=True)
        click.echo("'adxp-cli auth login' 명령어로 로그인하세요.", err=True)
        ctx.exit(1)


@cli.command()
@click.option('--name', required=True, help='Dataset 이름')
@click.option('--project-id', required=True, help='프로젝트 ID')
@click.option('--description', help='Dataset 설명')
@click.option('--dataset-type', type=click.Choice(['unsupervised_finetuning', 'supervised_finetuning', 'model_benchmark', 'dpo_finetuning', 'custom']), required=True, help='Dataset 타입')
@click.option('--files', help='업로드할 파일 경로들 (쉼표로 구분)')
@click.option('--datasource-id', help='기존 데이터소스 ID (파일 없이 생성할 때)')
@click.option('--tags', help='Dataset 태그 (쉼표로 구분)')
@click.option('--processor-ids', help='프로세서 ID들 (쉼표로 구분)')
@click.option('--duplicate-columns', help='중복 제거 대상 컬럼들 (쉼표로 구분)')
@click.option('--regex-patterns', help='정규표현식 패턴들 (쉼표로 구분)')
@click.pass_context
def create(ctx, name: str, project_id: str, description: str, dataset_type: str, 
          files: str, datasource_id: str, tags: str, processor_ids: str, duplicate_columns: str, regex_patterns: str):
    """Dataset 생성 (파일 업로드 포함)"""
    client = ctx.obj['client']
    
    # 태그 처리
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
    
    # 프로세서 처리 (빈 배열 필드 제거)
    processor = None
    if processor_ids or duplicate_columns or regex_patterns:
        processor_data = {}
        if processor_ids:
            processor_data["ids"] = [pid.strip() for pid in processor_ids.split(',')]
        if duplicate_columns:
            processor_data["duplicate_subset_columns"] = [col.strip() for col in duplicate_columns.split(',')]
        if regex_patterns:
            processor_data["regular_expression"] = [pattern.strip() for pattern in regex_patterns.split(',')]
        
        # 빈 배열 필드 제거
        processor_data = {k: v for k, v in processor_data.items() if v}
        if processor_data:
            processor = DatasetProcessor(**processor_data)
    
    try:
        if files:
            # 파일이 있는 경우: 전체 플로우 실행
            file_paths = [path.strip() for path in files.split(',')]
            result = client.create_dataset_with_files(
                name=name,
                description=description or "",
                project_id=project_id,
                file_paths=file_paths,
                dataset_type=DatasetType(dataset_type),
                tags=tag_list,
                processor=processor
            )
        else:
            # 파일이 없는 경우: 기존 방식
            dataset_data = DatasetCreateRequest(
                name=name,
                description=description or "",
                project_id=project_id,
                type=DatasetType(dataset_type),
                tags=[{"name": tag} for tag in tag_list],
                datasource_id=datasource_id,
                processor=processor,
                is_deleted=False,
                created_by="",
                updated_by="",
                policy=[]
            )
            result = client.create_dataset(dataset_data)
        
        click.echo(f"Dataset 생성 성공: {result.get('id')}")
    except Exception as e:
        click.echo(f"Dataset 생성 실패: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.option('--project-id', required=True, help='프로젝트 ID')
@click.option('--page', default=1, help='페이지 번호')
@click.option('--size', default=10, help='페이지 크기')
@click.option('--sort', help='정렬 기준 (created_at, updated_at, name)')
@click.option('--dataset-type', help='Dataset 타입 필터')
@click.option('--status', help='상태 필터 (processing, completed, failed, canceled)')
@click.option('--tags', help='태그 필터 (쉼표로 구분)')
@click.option('--search', help='검색어')
@click.option('--verbose', '-v', is_flag=True, help='상세 정보 출력')
@click.pass_context
def list(ctx, project_id: str, page: int, size: int, sort: str, dataset_type: str, 
         status: str, tags: str, search: str, verbose: bool):
    """Dataset 목록 조회"""
    client = ctx.obj['client']
    
    # 필터 구성
    filter_obj = None
    if dataset_type or status or tags:
        filter_dict = {}
        if dataset_type:
            filter_dict['dataset_type'] = dataset_type
        if status:
            filter_dict['status'] = status
        if tags:
            filter_dict['tags'] = [tag.strip() for tag in tags.split(',')]
        filter_obj = DatasetFilter(**filter_dict)
    
    try:
        result = client.get_datasets(
            project_id=project_id,
            page=page,
            size=size,
            sort=sort,
            filter=filter_obj,
            search=search
        )
        
        if verbose:
            # 상세 정보 출력
            click.echo("=== Dataset 목록 조회 결과 ===")
            click.echo(f"응답 코드: {result.get('code', 'N/A')}")
            click.echo(f"응답 메시지: {result.get('detail', 'N/A')}")
            
            datasets = result.get('data', [])
            if datasets:
                click.echo(f"\n총 {len(datasets)}개의 Dataset:")
                for i, dataset in enumerate(datasets, 1):
                    click.echo(f"\n{i}. {dataset.get('name', 'N/A')}")
                    click.echo(f"   ID: {dataset.get('id', 'N/A')}")
                    click.echo(f"   타입: {dataset.get('dataset_type', 'N/A')}")
                    click.echo(f"   상태: {dataset.get('status', 'N/A')}")
                    click.echo(f"   설명: {dataset.get('description', 'N/A')}")
                    click.echo(f"   생성일: {dataset.get('created_at', 'N/A')}")
                    if dataset.get('tags'):
                        tag_names = [tag.get('tag', '') for tag in dataset.get('tags', [])]
                        click.echo(f"   태그: {', '.join(tag_names)}")
            else:
                click.echo("\nDataset이 없습니다.")
        else:
            # 간단한 정보만 출력
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
            
    except Exception as e:
        click.echo(f"Dataset 목록 조회 실패: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument('dataset_id')
@click.pass_context
def get(ctx, dataset_id: str):
    """특정 Dataset 조회"""
    client = ctx.obj['client']
    
    try:
        result = client.get_dataset(dataset_id)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"Dataset 조회 실패: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument('dataset_id')
@click.option('--description', help='Dataset 설명')
@click.option('--project-id', help='프로젝트 ID')
@click.option('--tags', help='Dataset 태그 (쉼표로 구분)')
@click.pass_context
def update(ctx, dataset_id: str, description: str, project_id: str, tags: str):
    """Dataset 수정 (description, project_id, tags만 수정 가능)"""
    client = ctx.obj['client']
    
    # 수정할 데이터 구성 (API 스펙에 맞춤)
    update_data = {}
    
    if description:
        update_data["description"] = description
    if project_id:
        update_data["project_id"] = project_id
    
    # 태그 처리 (API 스펙에 맞춤)
    if tags:
        tag_list = []
        for tag in tags.split(","):
            tag_list.append({"name": tag.strip()})
        update_data["tags"] = tag_list
    
    try:
        result = client.update_dataset(dataset_id, update_data)
        click.echo(f"Dataset 수정 성공: {result.get('id')}")
    except Exception as e:
        click.echo(f"Dataset 수정 실패: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument('dataset_id')
@click.option('--tags', required=True, help='Dataset 태그 (쉼표로 구분)')
@click.pass_context
def update_tags(ctx, dataset_id: str, tags: str):
    """Dataset 태그 수정"""
    client = ctx.obj['client']
    
    # 태그 처리 (API 스펙에 맞춤)
    tag_list = []
    for tag in tags.split(","):
        tag_list.append({"name": tag.strip()})
    
    try:
        result = client.update_dataset_tags(dataset_id, tag_list)
        click.echo(f"Dataset 태그 수정 성공: {result}")
    except Exception as e:
        click.echo(f"Dataset 태그 수정 실패: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument('dataset_id')
@click.pass_context
def delete(ctx, dataset_id: str):
    """Dataset 삭제 (논리적 삭제 - is_deleted=True로 설정)"""
    client = ctx.obj['client']
    
    try:
        result = client.delete_dataset(dataset_id)
        click.echo(f"Dataset 삭제 성공: {dataset_id}")
    except Exception as e:
        click.echo(f"Dataset 삭제 실패: {e}", err=True)
        ctx.exit(1)


# ====================================================================
# 특별한 Dataset 타입별 생성 명령어
# ====================================================================

@cli.command()
@click.option('--name', required=True, help='Dataset 이름')
@click.option('--project-id', required=True, help='프로젝트 ID')
@click.option('--description', help='Dataset 설명')
@click.option('--datasource-id', required=True, help='데이터 소스 ID')
@click.option('--tags', help='Dataset 태그 (쉼표로 구분)')
@click.pass_context
def create_dpo(ctx, name: str, project_id: str, description: str, datasource_id: str, tags: str):
    """DPO Finetuning Dataset 생성 (실제 API 스펙에 맞춤)"""
    client = ctx.obj['client']
    
    tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
    
    try:
        result = client.create_dpo_dataset(name, description or "", project_id, datasource_id, tag_list)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"DPO Dataset 생성 실패: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.option('--name', required=True, help='Dataset 이름')
@click.option('--project-id', required=True, help='프로젝트 ID')
@click.option('--description', help='Dataset 설명')
@click.option('--tags', help='Dataset 태그 (쉼표로 구분)')
@click.pass_context
def create_custom(ctx, name: str, project_id: str, description: str, tags: str):
    """Custom Dataset 생성 (Data source 없이)"""
    client = ctx.obj['client']
    
    tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
    
    try:
        result = client.create_custom_dataset(name, description or "", project_id, tag_list)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"Custom Dataset 생성 실패: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.option('--name', required=True, help='Dataset 이름')
@click.option('--project-id', required=True, help='프로젝트 ID')
@click.option('--description', help='Dataset 설명')
@click.option('--datasource-id', required=True, help='데이터 소스 ID')
@click.option('--tags', help='Dataset 태그 (쉼표로 구분)')
@click.pass_context
def create_benchmark(ctx, name: str, project_id: str, description: str, datasource_id: str, tags: str):
    """Model Benchmark Dataset 생성 (실제 API 스펙에 맞춤)"""
    client = ctx.obj['client']
    
    tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
    
    try:
        result = client.create_model_benchmark_dataset(name, description or "", project_id, datasource_id, tag_list)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"Model Benchmark Dataset 생성 실패: {e}", err=True)
        ctx.exit(1)


# ====================================================================
# 파일 업로드 관련 명령어
# ====================================================================

@cli.command()
@click.argument('file_path')
@click.option('--dataset-id', help='Dataset ID (선택사항)')
@click.pass_context
def upload(ctx, file_path: str, dataset_id: str):
    """파일 업로드"""
    client = ctx.obj['client']
    
    try:
        result = client.upload_file(file_path, dataset_id)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"파일 업로드 실패: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument('file_paths', nargs=-1)
@click.option('--dataset-id', help='Dataset ID (선택사항)')
@click.pass_context
def upload_multiple(ctx, file_paths: tuple, dataset_id: str):
    """여러 파일 업로드"""
    client = ctx.obj['client']
    
    try:
        result = client.upload_multiple_files(list(file_paths), dataset_id)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"다중 파일 업로드 실패: {e}", err=True)
        ctx.exit(1)


# ====================================================================
# 데이터 프로세서 관련 명령어
# ====================================================================

@cli.command()
@click.pass_context
def list_processors(ctx):
    """사용 가능한 데이터 프로세서 목록 조회"""
    client = ctx.obj['client']
    
    try:
        result = client.get_available_processors()
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"프로세서 목록 조회 실패: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument('dataset_id')
@click.option('--processors', required=True, help='적용할 프로세서들 (쉼표로 구분)')
@click.pass_context
def apply_processors(ctx, dataset_id: str, processors: str):
    """Dataset에 데이터 프로세서 적용"""
    client = ctx.obj['client']
    
    processor_list = []
    for processor in processors.split(","):
        processor_type = processor.strip()
        if processor_type in [p.value for p in DataProcessorType]:
            processor_list.append(DatasetProcessor(
                processor_type=DataProcessorType(processor_type),
                enabled=True
            ))
        else:
            click.echo(f"Warning: 알 수 없는 프로세서 타입: {processor_type}", err=True)
    
    try:
        result = client.apply_processors(dataset_id, processor_list)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"프로세서 적용 실패: {e}", err=True)
        ctx.exit(1)


if __name__ == '__main__':
    cli()