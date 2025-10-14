"""
Prompt CLI

Click 기반의 명령줄 인터페이스입니다.
핵심 CRUD 기능만 제공합니다.
"""

import click
import json
import os
from typing import Optional, List

try:
    from adxp_sdk.prompts.prompt_client import PromptClient
    from adxp_sdk.prompts.prompt_schemas import PromptCreateRequest, PromptUpdateRequest
except ImportError:
    # 직접 실행할 때를 위한 절대 import
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sdk'))
    from adxp_sdk.prompts.prompt_client import PromptClient
    from adxp_sdk.prompts.prompt_schemas import PromptCreateRequest, PromptUpdateRequest


@click.group()
@click.option('--api-key', envvar='PROMPT_API_KEY', help='API 키 (선택사항, 기본적으로 저장된 인증 정보 사용)')
@click.pass_context
def prompts(ctx, api_key: str):
    """Prompt CRUD CLI - 핵심 CRUD 기능만 제공"""
    ctx.ensure_object(dict)
    
    try:
        if api_key:
            # API 키가 제공된 경우 직접 사용
            from adxp_cli.auth.service import get_credential
            headers, config = get_credential()
            client = PromptClient(f"{config.base_url}/api/v1/agent", api_key)
        else:
            # 저장된 인증 정보 사용
            from adxp_cli.auth.service import get_credential
            headers, config = get_credential()
            client = PromptClient(f"{config.base_url}/api/v1/agent", config.token)
        
        ctx.obj['client'] = client
        click.echo("✅ 인증 성공!")
        
    except Exception as e:
        click.echo(f"Error: 인증 실패 - {e}", err=True)
        click.echo("💡 먼저 'adxp auth login' 명령어로 로그인하세요.", err=True)
        ctx.exit(1)


@prompts.command()
@click.option('--name', required=True, help='프롬프트 이름')
@click.option('--project-id', help='프로젝트 ID (기본값: 인증된 프로젝트)')
@click.option('--description', help='프롬프트 설명')
@click.option('--system-prompt', help='시스템 프롬프트')
@click.option('--user-prompt', help='사용자 프롬프트')
@click.option('--assistant-prompt', help='어시스턴트 프롬프트')
@click.option('--tags', help='프롬프트 태그 (쉼표로 구분)')
@click.option('--variables', help='프롬프트 변수 (쉼표로 구분)')
@click.option('--template', help='템플릿 이름 (예: AGENT__GENERATOR)')
@click.option('--release', type=bool, help='릴리즈 여부')
@click.pass_context
def create(ctx, name: str, project_id: str, description: str, system_prompt: str, 
          user_prompt: str, assistant_prompt: str, tags: str, variables: str, 
          template: str, release: Optional[bool]):
    """프롬프트 생성"""
    client = ctx.obj['client']
    
    # project_id가 없으면 인증된 프로젝트 사용
    if not project_id:
        from adxp_cli.auth.service import get_credential
        _, config = get_credential()
        project_id = config.client_id  # client_id를 프로젝트로 사용
    
    # 프롬프트 데이터 구성
    prompt_data = {
        "name": name,
        "project_id": project_id,
        "release": release if release is not None else False
    }
    
    if description:
        prompt_data["desc"] = description
    
    # 템플릿 사용
    if template:
        prompt_data["template"] = template
    else:
        # 직접 메시지 구성
        messages = []
        if system_prompt:
            messages.append({"message": system_prompt, "mtype": 1})
        if user_prompt:
            messages.append({"message": user_prompt, "mtype": 2})
        if assistant_prompt:
            messages.append({"message": assistant_prompt, "mtype": 3})
        
        if not messages:
            click.echo("Error: 프롬프트 생성 시 최소 하나의 메시지가 필요합니다.", err=True)
            click.echo("  --system-prompt, --user-prompt, --assistant-prompt 중 하나를 입력하거나", err=True)
            click.echo("  --template 옵션을 사용하세요.", err=True)
            ctx.exit(1)
        
        prompt_data["messages"] = messages
        
        # 태그 구성
        if tags:
            tag_list = []
            for tag in tags.split(","):
                tag_list.append({"tag": tag.strip()})
            prompt_data["tags"] = tag_list
        
        # 변수 구성
        if variables:
            variable_list = []
            for var in variables.split(","):
                variable_list.append({
                    "variable": var.strip(),
                    "token_limit": 0,
                    "token_limit_flag": False,
                    "validation": "",
                    "validation_flag": False
                })
            prompt_data["variables"] = variable_list
    
    try:
        result = client.create_prompt(prompt_data)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"프롬프트 생성 실패: {e}", err=True)
        ctx.exit(1)


@prompts.command()
@click.option('--project-id', help='프로젝트 ID (기본값: 인증된 프로젝트)')
@click.option('--page', default=1, help='페이지 번호')
@click.option('--size', default=10, help='페이지 크기')
@click.option('--sort', help='정렬 기준 (created_at, updated_at, name)')
@click.option('--filter', help='필터 조건')
@click.option('--search', help='검색어')
@click.option('--verbose', '-v', is_flag=True, help='상세 정보 출력')
@click.pass_context
def list(ctx, project_id: str, page: int, size: int, sort: str, filter: str, search: str, verbose: bool):
    """프롬프트 목록 조회"""
    client = ctx.obj['client']
    
    # project_id가 없으면 인증된 프로젝트 사용
    if not project_id:
        from adxp_cli.auth.service import get_credential
        _, config = get_credential()
        project_id = config.client_id  # client_id를 프로젝트로 사용
    
    try:
        result = client.get_prompts(
            project_id=project_id,
            page=page,
            size=size,
            sort=sort,
            filter=filter,
            search=search
        )
        
        if verbose:
            # 상세 정보 출력
            click.echo("=== 프롬프트 목록 조회 결과 ===")
            click.echo(f"응답 코드: {result.get('code', 'N/A')}")
            click.echo(f"응답 메시지: {result.get('detail', 'N/A')}")
            
            prompts = result.get('data', [])
            if prompts:
                click.echo(f"\n총 {len(prompts)}개의 프롬프트:")
                for i, prompt in enumerate(prompts, 1):
                    click.echo(f"\n{i}. {prompt.get('name', 'N/A')}")
                    click.echo(f"   UUID: {prompt.get('uuid', 'N/A')}")
                    click.echo(f"   설명: {prompt.get('desc', 'N/A')}")
                    click.echo(f"   생성일: {prompt.get('created_at', 'N/A')}")
                    if prompt.get('tags'):
                        tags = [tag.get('tag', '') for tag in prompt.get('tags', [])]
                        click.echo(f"   태그: {', '.join(tags)}")
            else:
                click.echo("\n프롬프트가 없습니다.")
        else:
            # 간단한 정보만 출력
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
            
    except Exception as e:
        click.echo(f"프롬프트 목록 조회 실패: {e}", err=True)
        ctx.exit(1)


@prompts.command()
@click.argument('prompt_uuid', required=True)
@click.pass_context
def get(ctx, prompt_uuid: str):
    """특정 프롬프트 조회"""
    client = ctx.obj['client']
    
    try:
        result = client.get_prompt(prompt_uuid)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"프롬프트 조회 실패: {e}", err=True)
        ctx.exit(1)


@prompts.command()
@click.argument('prompt_uuid', required=True)
@click.option('--name', help='프롬프트 이름')
@click.option('--description', help='프롬프트 설명')
@click.option('--system-prompt', help='시스템 프롬프트')
@click.option('--user-prompt', help='사용자 프롬프트')
@click.option('--assistant-prompt', help='어시스턴트 프롬프트')
@click.option('--tags', help='프롬프트 태그 (쉼표로 구분)')
@click.option('--variables', help='프롬프트 변수 (쉼표로 구분)')
@click.option('--release', type=bool, help='릴리즈 여부')
@click.pass_context
def update(ctx, prompt_uuid: str, name: str, description: str, system_prompt: str,
          user_prompt: str, assistant_prompt: str, tags: str, variables: str, release: bool):
    """프롬프트 수정"""
    client = ctx.obj['client']
    
    # 수정할 데이터 구성 (API 형식에 맞춤)
    update_data = {}
    
    if name:
        update_data["new_name"] = name  # name 대신 new_name 사용
    
    if description:
        update_data["desc"] = description  # description 대신 desc 사용
    
    # 메시지 구성
    messages = []
    if system_prompt:
        messages.append({"message": system_prompt, "mtype": 1})
    if user_prompt:
        messages.append({"message": user_prompt, "mtype": 2})
    if assistant_prompt:
        messages.append({"message": assistant_prompt, "mtype": 3})
    
    if messages:
        update_data["messages"] = messages
    
    # 태그 구성
    if tags:
        tag_list = []
        for tag in tags.split(","):
            tag_list.append({"tag": tag.strip()})
        update_data["tags"] = tag_list
    
    # 변수 구성
    if variables:
        variable_list = []
        for var in variables.split(","):
            variable_list.append({
                "variable": var.strip(),
                "token_limit": 0,
                "token_limit_flag": False,
                "validation": "",
                "validation_flag": False
            })
        update_data["variables"] = variable_list
    
    if release is not None:
        update_data["release"] = release
    
    try:
        result = client.update_prompt(prompt_uuid, update_data)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"프롬프트 수정 실패: {e}", err=True)
        ctx.exit(1)


@prompts.command()
@click.argument('prompt_uuid', required=True)
@click.pass_context
def delete(ctx, prompt_uuid: str):
    """프롬프트 삭제"""
    client = ctx.obj['client']
    
    try:
        result = client.delete_prompt(prompt_uuid)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"프롬프트 삭제 실패: {e}", err=True)
        ctx.exit(1)


if __name__ == "__main__":
    cli()