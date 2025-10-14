import click
import json
from adxp_cli.auth.service import get_credential
from adxp_sdk.authorization.hub import AXAuthorizationHub


# ====================================================================
# Project Commands
# ====================================================================

@click.group(name="project")    
def project():
    """Manage Projects."""
    pass


# -- Projects CRUD ---------------------------------------------------

# List all projects
@project.command(name="list")
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
@click.option("--json-output", is_flag=True, help="Output raw JSON")
def list_projects(page, size, json_output):
    """List Projects from the A.X Platform"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        projects = hub.list_projects(page=page, size=size)

        if json_output:
            click.echo(json.dumps(projects, indent=2))
        else:
            click.secho("📂 Project List:", fg="cyan")
            data = projects.get("data", [])
            if not data:
                click.secho("No projects found.", fg="yellow")
            for idx, item in enumerate(data, 1):
                name = item.get("project", {}).get("name", "N/A")
                click.echo(f"{idx}. {name}")

        return projects

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again.\n Run: adxp-cli auth login"
            )
        raise click.ClickException(f"❌ Failed to list projects: {e}")


# Create a new project
@project.command(name="create")
@click.option("--name", prompt="Project name", help="생성할 프로젝트 이름")
@click.option("--node-type", default="task", help="노드 타입 (기본값: task)")
def create_project(name, node_type):
    """Create a new Project in the A.X Platform"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        resource_info = hub.get_project_resource_status(node_type=node_type)
        cluster = resource_info.get("cluster_resource", {})

        click.secho("Available Cluster Resource:", fg="cyan")
        click.echo(
            f"CPU: {cluster.get('cpu_used')}/{cluster.get('cpu_total')} "
            f"(Usable: {cluster.get('cpu_usable')})"
        )
        click.echo(
            f"Memory: {cluster.get('memory_used')}/{cluster.get('memory_total')} "
            f"(Usable: {cluster.get('memory_usable')})"
        )
        click.echo(
            f"GPU: {cluster.get('gpu_used')}/{cluster.get('gpu_total')} "
            f"(Usable: {cluster.get('gpu_usable')})"
        )

        click.echo()
        click.secho("Enter resource quota values below:", fg="yellow")
        click.echo("-----------------------------------------")

        cpu_quota = click.prompt("CPU quota (Core)", type=int)
        mem_quota = click.prompt("Memory quota (GB)", type=int)
        gpu_quota = click.prompt("GPU quota (Core)", type=int)

        project = hub.create_project(
            name=name, cpu_quota=cpu_quota, mem_quota=mem_quota, gpu_quota=gpu_quota
        )
        click.secho(
            f"✅ Project Created! ID={project.get('project', {}).get('id')} "
            f"Name={project.get('project', {}).get('name')}",
            fg="green",
        )

    except Exception as e:
        raise click.ClickException(f"❌ Failed to create project: {e}")


# Update an existing project
@project.command(name="update")
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
@click.argument("name", required=False)
@click.option("--node-type", default="task", help="노드 타입 (기본값: task)")
def update_project(page, size, name, node_type):
    """Update an existing Project in the A.X Platform"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        selected = None

        if name:
            # name 직접 입력 → 전체 페이지 탐색
            search_page = 1
            while True:
                projects = hub.list_projects(page=search_page, size=size)
                data = projects.get("data", [])
                if not data:
                    break
                for item in data:
                    if item.get("project", {}).get("name") == name:
                        selected = item
                        break
                if selected:
                    break
                search_page += 1

            if not selected:
                click.secho(f"❌ 프로젝트 '{name}' 를 찾을 수 없습니다.", fg="red")
                return
        else:
            # 리스트 출력 모드
            projects = hub.list_projects(page=page, size=size)
            data = projects.get("data", [])
            if not data:
                click.secho("⚠️ No projects found.", fg="yellow")
                return

            click.secho("📂 Project List:", fg="cyan")
            for idx, item in enumerate(data, 1):
                pid = item.get("project", {}).get("id")
                pname = item.get("project", {}).get("name", "N/A")
                click.echo(f"{idx}. {pname} (ID={pid})")

            choice = click.prompt("수정할 프로젝트 선택 (번호 또는 이름)")
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(data):
                    selected = data[idx - 1]
            else:
                for item in data:
                    if item.get("project", {}).get("name") == choice:
                        selected = item
                        break

            if not selected:
                click.secho("❌ 잘못된 입력입니다. 다시 시도해주세요.", fg="red")
                return

        project_id = selected.get("project", {}).get("id")
        current_name = selected.get("project", {}).get("name", "")

        # 클러스터 리소스 출력
        resource_info = hub.get_project_resource_status(node_type=node_type)
        cluster = resource_info.get("cluster_resource", {})

        click.secho("\n🖥️ Available Cluster Resource:", fg="cyan")
        click.echo(
            f"CPU: {cluster.get('cpu_used')}/{cluster.get('cpu_total')} (Usable: {cluster.get('cpu_usable')})"
        )
        click.echo(
            f"Memory: {cluster.get('memory_used')}/{cluster.get('memory_total')} (Usable: {cluster.get('memory_usable')})"
        )
        click.echo(
            f"GPU: {cluster.get('gpu_used')}/{cluster.get('gpu_total')} (Usable: {cluster.get('gpu_usable')})"
        )

        click.echo()
        click.secho("🔽 Enter new values below (press Enter to keep current):", fg="yellow")
        click.echo("----------------------------------------------------------")

        new_name = click.prompt("Project name", default=current_name, show_default=True)
        cpu_quota = click.prompt("CPU quota", type=int)
        mem_quota = click.prompt("Memory quota (GB)", type=int)
        gpu_quota = click.prompt("GPU quota", type=int)

        project = hub.update_project(
            project_id=project_id,
            name=new_name,
            cpu_quota=cpu_quota,
            mem_quota=mem_quota,
            gpu_quota=gpu_quota,
        )

        click.secho(
            f"✅ Project Updated! ID={project.get('project', {}).get('id')} "
            f"Name={project.get('project', {}).get('name')}",
            fg="green",
        )

    except Exception as e:
        raise click.ClickException(f"❌ Failed to update project: {e}")


# Delete a project
@project.command(name="delete")
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
@click.argument("name", required=False)
def delete_project(page, size, name):
    """Delete a Project from the A.X Platform"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        selected = None

        if name:
            # name 직접 입력 → 전체 페이지 탐색
            search_page = 1
            while True:
                projects = hub.list_projects(page=search_page, size=size)
                data = projects.get("data", [])
                if not data:
                    break
                for item in data:
                    if item.get("project", {}).get("name") == name:
                        selected = item
                        break
                if selected:
                    break
                search_page += 1

            if not selected:
                click.secho(f"❌ 프로젝트 '{name}' 를 찾을 수 없습니다.", fg="red")
                return
        else:
            # 리스트 출력 모드
            projects = hub.list_projects(page=page, size=size)
            data = projects.get("data", [])
            if not data:
                click.secho("⚠️ No projects found.", fg="yellow")
                return

            click.secho("📂 Project List:", fg="cyan")
            for idx, item in enumerate(data, 1):
                pid = item.get("project", {}).get("id")
                pname = item.get("project", {}).get("name", "N/A")
                click.echo(f"{idx}. {pname} (ID={pid})")

            choice = click.prompt("삭제할 프로젝트 선택 (번호 또는 이름)")
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(data):
                    selected = data[idx - 1]
            else:
                for item in data:
                    if item.get("project", {}).get("name") == choice:
                        selected = item
                        break

            if not selected:
                click.secho("❌ 잘못된 입력입니다. 다시 시도해주세요.", fg="red")
                return

        project_id = selected.get("project", {}).get("id")
        project_name = selected.get("project", {}).get("name")

        confirm = click.confirm(
            f"정말로 프로젝트 '{project_name}' (ID={project_id}) 를 삭제하시겠습니까?",
            default=False,
        )
        if not confirm:
            click.secho("🚫 삭제 취소됨", fg="yellow")
            return

        result = hub.delete_project(project_id=project_id)

        click.secho(
            f"🗑️ Project Deleted! ID={result.get('project', {}).get('id', project_id)} "
            f"Name={result.get('project', {}).get('name', project_name)}",
            fg="red",
        )

    except Exception as e:
        raise click.ClickException(f"❌ Failed to delete project: {e}")


# ====================================================================
# Role Commands (Project 하위)
# ====================================================================

@project.group(name="role")
def role():
    """Manage Roles within a Project"""
    pass


# -- Roles CRUD ------------------------------------------------------

# List roles in the current project
@role.command(name="list")
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
@click.option("--json-output", is_flag=True, help="Output raw JSON")
def list_roles(page, size, json_output):
    """List roles in the current project"""
    try:
        headers, config = get_credential()

        client_id = getattr(config, "client_id", None)
        project_name = getattr(config, "project_name", None)

        if not client_id:
            raise click.ClickException("❌ 현재 로그인된 프로젝트가 없습니다. 'adxp-cli auth login' 또는 'auth exchange'를 먼저 실행하세요.")

        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)
        roles = hub.list_project_roles(client_id=client_id, page=page, size=size)

        if json_output:
            click.echo(json.dumps(roles, indent=2))
            return roles

        click.secho(f"👥 Roles for Project {project_name or client_id}:", fg="cyan")

        data = roles.get("data", [])
        if not data:
            click.secho("No roles found.", fg="yellow")
            return roles

        for idx, item in enumerate(data, 1):
            role_name = item.get("name") or "N/A"
            role_id = item.get("id") or "N/A"
            click.echo(f"{idx}. {role_name} (ID={role_id})")

        return roles
    except Exception as e:
        raise click.ClickException(f"❌ Failed to list roles: {e}")


# Create a role in the current project
@role.command(name="create")
@click.option("--name", prompt="Role name", help="생성할 Role 이름")
@click.option("--description", default="", prompt="Role description", help="Role description")
def create_role(name, description):
    """Create a new role in the current project"""
    try:
        headers, config = get_credential()

        client_id = getattr(config, "client_id", None)
        project_name = getattr(config, "project_name", None)

        if not client_id:
            raise click.ClickException("❌ 현재 로그인된 프로젝트가 없습니다. 'adxp-cli auth login' 또는 'auth exchange'를 먼저 실행하세요.")

        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)
        role = hub.create_project_role(client_id=client_id, name=name, description=description)

        click.secho(
            f"✅ Role Created! Project={project_name or client_id} "
            f"RoleName={role.get('name')} (ID={role.get('id')})",
            fg="green",
        )

        return role

    except Exception as e:
        raise click.ClickException(f"❌ Failed to create role: {e}")


# Update an existing role's description
@role.command(name="update")
@click.argument("role_name", required=False)
@click.option("--description", prompt=False, help="새로운 description (prompt 생략 가능)")
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
def update_role(role_name, description, page, size):
    """Update an existing role's description"""
    try:
        headers, config = get_credential()
        client_id = getattr(config, "client_id", None)
        if not client_id:
            raise click.ClickException("❌ client_id가 없습니다. 로그인 정보를 확인하세요.")

        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        selected = None

        # role_name 없으면 → 리스트 출력 후 선택
        roles = hub.list_project_roles(client_id=client_id, page=page, size=size)
        data = roles.get("data", [])
        if not data:
            click.secho("⚠️ No roles found.", fg="yellow")
            return

        if not role_name:
            click.secho("📋 Available Roles:", fg="cyan")
            for idx, item in enumerate(data, 1):
                rname = item.get("name") or "N/A"
                rdesc = item.get("description") or "-"
                click.echo(f"{idx}. {rname} | desc={rdesc}")
                
            choice = click.prompt("수정할 role 선택 (번호 또는 이름)")
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(data):
                    selected = data[idx - 1]
            else:
                selected = next((r for r in data if r.get("name") == choice), None)

            if not selected:
                click.secho("❌ 잘못된 입력입니다. 다시 시도해주세요.", fg="red")
                return

        else:
            # role_name 직접 지정된 경우 → 데이터 안에서 찾기
            selected = next((r for r in data if r.get("name") == role_name), None)
            if not selected:
                click.secho(f"❌ '{role_name}' role을 찾을 수 없습니다.", fg="red")
                return

        role_name = selected.get("name")
        current_desc = selected.get("description") or ""

        # description 없으면 → 기존값 보여주고 프롬프트
        if not description:
            description = click.prompt(
                "새로운 description", default=current_desc, show_default=True
            )

        role = hub.update_project_role(
            client_id=client_id, role_name=role_name, description=description
        )

        click.secho(
            f"✅ Role Updated! Name={role_name}, Description={description}",
            fg="green",
        )

        return role

    except Exception as e:
        raise click.ClickException(f"❌ Failed to update role: {e}")
    

# Delete a role from the current project
@role.command(name="delete")
@click.argument("role_name", required=False)
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
def delete_role(role_name, page, size):
    """Delete a role from the current project"""
    try:
        headers, config = get_credential()
        client_id = getattr(config, "client_id", None)
        if not client_id:
            raise click.ClickException("❌ client_id가 없습니다. 로그인 정보를 확인하세요.")

        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        selected = None

        # role_name 없으면 → 리스트 출력 후 선택
        roles = hub.list_project_roles(client_id=client_id, page=page, size=size)
        data = roles.get("data", [])
        if not data:
            click.secho("⚠️ No roles found.", fg="yellow")
            return

        if not role_name:
            click.secho("📋 Available Roles:", fg="cyan")
            for idx, item in enumerate(data, 1):
                rname = item.get("name") or "N/A"
                rdesc = item.get("description") or "-"
                click.echo(f"{idx}. {rname} | desc={rdesc}")

            choice = click.prompt("삭제할 role 선택 (번호 또는 이름)")
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(data):
                    selected = data[idx - 1]
            else:
                selected = next((r for r in data if r.get("name") == choice), None)

            if not selected:
                click.secho("❌ 잘못된 입력입니다. 다시 시도해주세요.", fg="red")
                return
        else:
            # role_name 직접 지정된 경우 → 데이터 안에서 찾기
            selected = next((r for r in data if r.get("name") == role_name), None)
            if not selected:
                click.secho(f"❌ '{role_name}' role을 찾을 수 없습니다.", fg="red")
                return

        role_name = selected.get("name")
        role_desc = selected.get("description") or "-"

        # 삭제 확인
        confirm = click.confirm(
            f"정말로 role '{role_name}' (desc={role_desc}) 를 삭제하시겠습니까?",
            default=False,
        )
        if not confirm:
            click.secho("🚫 삭제 취소됨", fg="yellow")
            return

        result = hub.delete_project_role(client_id=client_id, role_name=role_name)

        click.secho(
            f"🗑️ Role Deleted! Name={role_name}",
            fg="red",
        )

        return result

    except Exception as e:
        raise click.ClickException(f"❌ Failed to delete role: {e}")
