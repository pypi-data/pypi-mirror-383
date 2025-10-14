import click
import json
from adxp_cli.auth.service import get_credential
from adxp_cli.authorization.utils import select_user, select_roles
from adxp_sdk.authorization.hub import AXAuthorizationHub


@click.group(name="user")
def user():
    """Manage Users."""
    pass


# ====================================================================
# List Users
# ====================================================================
@user.command(name="list")
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
@click.option("--json-output", is_flag=True, help="Output raw JSON")
def list_users(page, size, json_output):
    """List Users from the A.X Platform"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        users = hub.list_users(page=page, size=size)

        if json_output:
            click.echo(json.dumps(users, indent=2))
        else:
            click.secho("👤 User List:", fg="cyan")
            data = users.get("data", [])
            if not data:
                click.secho("No users found.", fg="yellow")
            for idx, item in enumerate(data, 1):
                username = item.get("username", "N/A")
                email = item.get("email", "N/A")
                click.echo(f"{idx}. {username} ({email})")

        return users

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again.\n Run: adxp-cli auth login"
            )
        raise click.ClickException(f"❌ Failed to list users: {e}")


# ====================================================================
# Create User
# ====================================================================
@user.command(name="create")
@click.option("--username", prompt=True, help="Username")
@click.option("--email", prompt=True, help="Email")
@click.option("--first-name", prompt=True, help="First name")
@click.option("--last-name", prompt=True, help="Last name")
def create_user(username, email, first_name, last_name):
    """Create a new user in the A.X Platform"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        # 비밀번호 입력 (두 번 확인)
        while True:
            password = click.prompt("Password", hide_input=True)
            confirm_password = click.prompt("Confirm Password", hide_input=True)

            if password != confirm_password:
                click.secho("❌ Passwords do not match. Please try again.", fg="red")
                continue
            if len(password) < 8:
                click.secho("❌ Password must be at least 8 characters.", fg="red")
                continue
            if (
                not any(c.islower() for c in password)
                or not any(c.isupper() for c in password)
                or not any(c.isdigit() for c in password)
                or not any(not c.isalnum() for c in password)
            ):
                click.secho(
                    "❌ Password must include upper/lower letters, numbers, and symbols.",
                    fg="red",
                )
                continue
            break

        user = hub.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        click.secho(
            f"✅ User Created! ID={user.get('id')} Username={user.get('username')}",
            fg="green",
        )

    except Exception as e:
        raise click.ClickException(f"❌ Failed to create user: {e}")


# ====================================================================
# Update User
# ====================================================================
@user.command(name="update")
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
@click.argument("username", required=False)
def update_user(page, size, username):
    """Update an existing User in the A.X Platform"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        selected = None

        if username:
            # username 직접 입력 → 전체 페이지 탐색
            search_page = 1
            while True:
                users = hub.list_users(page=search_page, size=size)
                data = users.get("data", [])
                if not data:
                    break
                for item in data:
                    if item.get("username") == username:
                        selected = item
                        break
                if selected:
                    break
                search_page += 1

            if not selected:
                click.secho(f"❌ 사용자 '{username}' 를 찾을 수 없습니다.", fg="red")
                return

        else:
            # 리스트 출력 모드
            users = hub.list_users(page=page, size=size)
            data = users.get("data", [])
            if not data:
                click.secho("⚠️ No users found.", fg="yellow")
                return

            selected = select_user(data)
            if not selected:
                return

        user_id = selected.get("id")
        current_email = selected.get("email") or ""
        current_first_name = selected.get("first_name") or ""
        current_last_name = selected.get("last_name") or ""

        # 입력 프롬프트
        email = click.prompt("Email", default=current_email, show_default=True)
        first_name = click.prompt("First name", default=current_first_name, show_default=True)
        last_name = click.prompt("Last name", default=current_last_name, show_default=True)

        # 업데이트 실행
        hub.update_user(user_id=user_id, email=email, first_name=first_name, last_name=last_name)

        click.secho(
            f"✅ User Updated! Username={selected.get('username')} Email={email}",
            fg="green",
        )

    except Exception as e:
        raise click.ClickException(f"❌ Failed to update user: {e}")


# ====================================================================
# Delete User
# ====================================================================
@user.command(name="delete")
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
@click.argument("username", required=False)
def delete_user(page, size, username):
    """Delete a User from the A.X Platform"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        selected = None

        if username:
            # username 직접 입력 → 전체 페이지 탐색
            search_page = 1
            while True:
                users = hub.list_users(page=search_page, size=size)
                data = users.get("data", [])
                if not data:
                    break
                for item in data:
                    if item.get("username") == username:
                        selected = item
                        break
                if selected:
                    break
                search_page += 1

            if not selected:
                click.secho(f"❌ 사용자 '{username}' 를 찾을 수 없습니다.", fg="red")
                return

        else:
            users = hub.list_users(page=page, size=size)
            data = users.get("data", [])
            if not data:
                click.secho("⚠️ No users found.", fg="yellow")
                return

            selected = select_user(data)
            if not selected:
                return

        user_id = selected.get("id")
        uname = selected.get("username")

        confirm = click.confirm(
            f"정말로 사용자 '{uname}' (ID={user_id}) 를 삭제하시겠습니까?",
            default=False,
        )
        if not confirm:
            click.secho("🚫 삭제 취소됨", fg="yellow")
            return

        hub.delete_user(user_id=user_id)

        click.secho(f"🗑️ User Deleted! Username={uname}", fg="red")

    except Exception as e:
        raise click.ClickException(f"❌ Failed to delete user: {e}")
    
# ====================================================================
# User: Show Assigned Roles
# ====================================================================
@user.command(name="role-assigned")
@click.argument("username", required=False)
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
def list_assigned_roles(username, page, size):
    """List roles currently assigned to a user"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        # 유저 선택
        if not username:
            users = hub.list_users(page=1, size=50).get("data", [])
            selected_user = select_user(users)
            if not selected_user:
                return
        else:
            selected_user = None
            search_page = 1
            while True:
                user_page = hub.list_users(page=search_page, size=10).get("data", [])
                if not user_page:
                    break
                for u in user_page:
                    if u.get("username") == username:
                        selected_user = u
                        break
                if selected_user:
                    break
                search_page += 1
            if not selected_user:
                click.secho(f"❌ 사용자 '{username}' 를 찾을 수 없습니다.", fg="red")
                return

        user_id = selected_user.get("id")
        username = selected_user.get("username")

        # 현재 부여된 roles 조회
        assigned = hub.list_user_assigned_roles(user_id=user_id, page=page, size=size)
        role_data = assigned.get("data", [])

        if not role_data:
            click.secho("⚠️ No assigned roles found.", fg="yellow")
            return

        click.secho(f"📋 Roles assigned to user '{username}':", fg="cyan")
        for idx, item in enumerate(role_data, 1):
            rname = item["role"].get("name")
            rdesc = item["role"].get("description") or "-"
            pname = item["project"].get("name")
            click.echo(f"{idx}. {rname} (Project={pname}, desc={rdesc})")

    except Exception as e:
        raise click.ClickException(f"❌ Failed to list assigned roles: {e}")



# ====================================================================
# User: Assign Roles
# ====================================================================
@user.command(name="role-assign")
@click.argument("username", required=False)
@click.option("--roles", multiple=True, help="Assign roles (name or index, comma-separated if prompt)")
@click.option("--page", default=1, help="Page number for users")
@click.option("--size", default=10, help="Page size for users")
@click.option("--role-page", default=1, help="Page number for roles")
@click.option("--role-size", default=10, help="Page size for roles")
def assign_roles(username, roles, page, size, role_page, role_size):
    """Assign one or more roles to a user in the current project"""
    try:
        headers, config = get_credential()
        client_id = getattr(config, "client_id", None)
        project_name = getattr(config, "project_name", None)

        if not client_id:
            raise click.ClickException("❌ 현재 로그인된 프로젝트가 없습니다. 'auth login' 또는 'auth exchange'를 먼저 실행하세요.")

        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        # 유저 선택
        if not username:
            users = hub.list_users(page=page, size=size).get("data", [])
            selected_user = select_user(users)
            if not selected_user:
                return
        else:
            # username 직접 입력
            selected_user = None
            search_page = 1
            while True:
                user_page = hub.list_users(page=search_page, size=size).get("data", [])
                if not user_page:
                    break
                for u in user_page:
                    if u.get("username") == username:
                        selected_user = u
                        break
                if selected_user:
                    break
                search_page += 1
            if not selected_user:
                click.secho(f"❌ 사용자 '{username}' 를 찾을 수 없습니다.", fg="red")
                return

        user_id = selected_user.get("id")
        username = selected_user.get("username")

        # assign 가능한 roles
        available = hub.list_user_available_roles(user_id=user_id, page=role_page, size=role_size)
        role_data = available.get("data", [])

        # role 선택
        selected_roles = select_roles(role_data) if not roles else []
        if roles:
            for r in roles:
                if r.isdigit() and 1 <= int(r) <= len(role_data):
                    selected_roles.append(role_data[int(r) - 1])
                else:
                    sel = next((item for item in role_data if item["role"].get("name") == r), None)
                    if sel:
                        selected_roles.append(sel)

        if not selected_roles:
            click.secho("🚫 선택된 role이 없습니다.", fg="red")
            return

        body = [
            {
                "project": {"id": item["project"].get("id"), "name": item["project"].get("name")},
                "role": {
                    "id": item["role"].get("id"),
                    "name": item["role"].get("name"),
                    "description": item["role"].get("description"),
                },
            }
            for item in selected_roles
        ]

        result = hub.assign_roles_to_user(user_id=user_id, roles=body)

        click.secho(
            f"✅ Assigned {len(selected_roles)} role(s) to user '{username}' in Project={project_name or client_id}",
            fg="green",
        )

        return result

    except Exception as e:
        raise click.ClickException(f"❌ Failed to assign roles: {e}")


# ====================================================================
# User: Delete Roles
# ====================================================================
@user.command(name="role-delete")
@click.argument("username", required=False)
@click.option("--roles", multiple=True, help="Delete roles (name or index, comma-separated if prompt)")
@click.option("--page", default=1, help="Page number for users")
@click.option("--size", default=10, help="Page size for users")
@click.option("--role-page", default=1, help="Page number for roles")
@click.option("--role-size", default=10, help="Page size for roles")
def delete_roles(username, roles, page, size, role_page, role_size):
    """Delete one or more roles from a user in the current project"""
    try:
        headers, config = get_credential()
        client_id = getattr(config, "client_id", None)
        project_name = getattr(config, "project_name", None)

        if not client_id:
            raise click.ClickException("❌ 현재 로그인된 프로젝트가 없습니다. 'auth login' 또는 'auth exchange'를 먼저 실행하세요.")

        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        # 1) 유저 선택
        if not username:
            users = hub.list_users(page=page, size=size).get("data", [])
            selected_user = select_user(users)
            if not selected_user:
                return
        else:
            selected_user = None
            search_page = 1
            while True:
                user_page = hub.list_users(page=search_page, size=size).get("data", [])
                if not user_page:
                    break
                for u in user_page:
                    if u.get("username") == username:
                        selected_user = u
                        break
                if selected_user:
                    break
                search_page += 1
            if not selected_user:
                click.secho(f"❌ 사용자 '{username}' 를 찾을 수 없습니다.", fg="red")
                return

        user_id = selected_user.get("id")
        username = selected_user.get("username")

        # 2) 현재 부여된 roles 조회
        assigned = hub.list_user_assigned_roles(user_id=user_id, page=role_page, size=role_size)
        role_data = assigned.get("data", [])

        if not role_data:
            click.secho("⚠️ No assigned roles found for this user.", fg="yellow")
            return

        # 3) 삭제할 roles 선택
        selected_roles = []
        if roles:
            # --roles 옵션 입력 처리
            flat_roles = []
            for r in roles:
                flat_roles.extend(r.split(","))
            roles = [r.strip() for r in flat_roles if r.strip()]

            for r in roles:
                sel = None
                if r.isdigit() and 1 <= int(r) <= len(role_data):
                    sel = role_data[int(r) - 1]
                else:
                    sel = next((item for item in role_data if item["role"].get("name") == r), None)
                if sel:
                    selected_roles.append(sel)
                else:
                    click.secho(f"⚠️ 잘못된 role 입력: {r}", fg="yellow")
        else:
            # 프롬프트 선택
            selected_roles = select_roles(role_data)

        if not selected_roles:
            click.secho("🚫 선택된 role이 없습니다.", fg="red")
            return

        # 4) API 호출 (한 개씩 반복)
        deleted = []
        for item in selected_roles:
            body = [
                {
                    "project": {
                        "id": item["project"].get("id"),
                        "name": item["project"].get("name"),
                    },
                    "role": {
                        "id": item["role"].get("id"),
                        "name": item["role"].get("name"),
                        "description": item["role"].get("description"),
                    },
                }
            ]
            hub.delete_roles_from_user(user_id=user_id, roles=body)
            deleted.append(item["role"].get("name"))

        # 5) 결과 출력
        click.secho(
            f"🗑️ Deleted {len(deleted)} role(s) from user '{username}' "
            f"in Project={project_name or client_id}: {', '.join(deleted)}",
            fg="yellow",
        )

    except Exception as e:
        raise click.ClickException(f"❌ Failed to delete roles: {e}")

