import click
import json
import os
from click import secho
from adxp_sdk.auth.credentials import Credentials
from adxp_cli.auth.service import get_config_file_path, load_config_file
from adxp_cli.auth.schema import AuthConfig
from adxp_sdk.authorization.hub import AXAuthorizationHub


@click.group()
def auth():
    """Command-line interface for AIP Authentication"""
    pass


@auth.command()
@click.option("--username", prompt=True, help="username")
@click.option("--password", prompt=True, hide_input=True, help="password")
@click.option("--project", prompt=True, help="Name of the project")
@click.option(
    "--base-url",
    prompt=True,
    default="https://aip.sktai.io",
    show_default=True,
    help="API base URL",
)
def login(username, password, project, base_url):
    """A.X Platform에 로그인하고 정보를 저장합니다."""
    try:
        credentials = Credentials(
            username=username, password=password, project=project, base_url=base_url
        )
        token = credentials.token

        # 로그인 후 프로젝트 목록 조회
        hub = AXAuthorizationHub(credentials=credentials)
        projects = hub.list_projects(page=1, size=100)
        data = projects.get("data", [])

        # project_name → project_id 매핑
        matched = next(
            (item for item in data if item.get("project", {}).get("name") == project),
            None
        )
        if not matched:
            raise RuntimeError(f"Project '{project}' not found")

        project_id = matched.get("project", {}).get("id")
        project_name = matched.get("project", {}).get("name")

        auth_config = AuthConfig(
            username=username,
            client_id=project_id,
            project_name=project_name,
            base_url=base_url,
            token=token,
        ).model_dump()
        adxp_config_path = get_config_file_path(make_dir=True)
        with open(adxp_config_path, "w") as f:
            json.dump(auth_config, f, indent=2)
        secho(
            "Login successful. Authentication information has been saved.", fg="green"
        )
    except Exception as e:
        secho(f"Login failed: {e}", fg="red")


@auth.command()
def refresh():
    """저장된 인증 정보를 사용해 토큰을 갱신하고 config 파일을 업데이트합니다."""
    try:
        adxp_config_path = get_config_file_path(make_dir=False)
        auth_config = load_config_file(adxp_config_path)
        secho("Enter your password to refresh the token.", fg="yellow")
        password = click.prompt("password", hide_input=True)
        credentials = Credentials(
            username=auth_config.username,
            password=password,
            project=auth_config.client_id,
            base_url=auth_config.base_url,
        )
        token = credentials.token
        auth_config.token = token
        with open(adxp_config_path, "w") as f:
            json.dump(auth_config.model_dump(), f, indent=2)
        secho("Token has been successfully refreshed.", fg="green")
    except FileNotFoundError:
        secho(
            "🔐 Authentication information file does not exist. Please login first.",
            fg="red",
        )
    except Exception as e:
        secho(f"Failed to refresh token: {e}", fg="red")


@auth.command()
def logout():
    """저장된 인증 정보를 삭제합니다."""
    adxp_config_path = get_config_file_path(make_dir=False)
    if not os.path.exists(adxp_config_path):
        secho(
            "Authentication information file does not exist. Please login first.",
            fg="red",
        )
        return
    os.remove(adxp_config_path)
    secho("🔐 Authentication information has been successfully deleted.", fg="green")
    
    
@auth.command()
@click.argument("project_name", required=False)
@click.option("--page", default=1, help="Page number (default=1)")
@click.option("--size", default=10, help="Page size (default=10)")
def exchange(project_name, page, size):
    """저장된 토큰을 다른 클라이언트 토큰으로 교환합니다."""
    try:
        adxp_config_path = get_config_file_path(make_dir=False)
        auth_config = load_config_file(adxp_config_path)

        # TokenCredentials를 사용하여 hub 생성
        from adxp_sdk.auth import TokenCredentials
        credentials = TokenCredentials(
            access_token=auth_config.token,
            refresh_token="",  # CLI에서는 refresh_token을 저장하지 않음
            base_url=auth_config.base_url
        )
        
        hub = AXAuthorizationHub(credentials=credentials)
        projects_json = hub.list_projects(page=page, size=size)
        data = projects_json.get("data", [])

        if not data:
            raise RuntimeError("No projects found.")

        project_names = [item.get("project", {}).get("name") for item in data]

        # 프로젝트명 없을 경우 → 리스트 출력 + 입력받기
        if not project_name:
            secho("Available projects:", fg="yellow")
            for i, item in enumerate(data, start=1):
                pname = item.get("project", {}).get("name")
                pid = item.get("project", {}).get("id")
                secho(f"  {i}. {pname} (ID={pid})", fg="cyan")

            choice = click.prompt("Enter project name or number", type=str)

            # 번호 입력한 경우 → 프로젝트명으로 변환
            if choice.isdigit():
                idx = int(choice)
                if idx < 1 or idx > len(data):
                    raise RuntimeError(f"'{choice}' is not a valid selection.")
                project_name = data[idx - 1].get("project", {}).get("name")
            else:
                if choice not in project_names:
                    raise RuntimeError(f"'{choice}' is not a valid project name.")
                project_name = choice
        else:
            # 프로젝트명 argument 검증
            if project_name not in project_names:
                raise RuntimeError(f"'{project_name}' is not a valid project name.")

        # project_name → project_id 매핑
        matched = next(
            (item for item in data if item.get("project", {}).get("name") == project_name),
            None
        )
        if not matched:
            raise RuntimeError(f"Project '{project_name}' not found")
        project_id = matched.get("project", {}).get("id")

        # 교환 요청
        resp = Credentials.exchange_token(
            auth_config.base_url,
            auth_config.token,
            project_name,
        )
        new_token = resp.get("access_token")
        if not new_token:
            raise RuntimeError("No access_token found in response")

        # 🔑 토큰 + 프로젝트 정보 같이 저장
        auth_config.token = new_token
        auth_config.client_id = project_id
        auth_config.project_name = project_name

        with open(adxp_config_path, "w") as f:
            json.dump(auth_config.model_dump(), f, indent=2)

        secho(f"🔄 Token exchange successful → Project: {project_name} (ID={project_id})", fg="green")

    except Exception as e:
        secho(f"Token exchange failed: {e}", fg="red")



__all__ = ["auth"]