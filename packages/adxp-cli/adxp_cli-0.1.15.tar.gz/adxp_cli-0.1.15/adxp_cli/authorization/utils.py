import click

def select_user(users: list):
    """Prompt the user to select a user from a list (번호 or username)"""
    if not users:
        click.secho("사용자 목록이 비어있습니다.", fg="red")
        return None

    click.secho("👥 Available Users:", fg="cyan")
    for idx, u in enumerate(users, 1):
        uname = u.get("username") or u.get("name") or "-"
        uid = u.get("id") or u.get("user_id") or "-"
        email = u.get("email") or "-"
        click.echo(f"{idx}. {uname} (ID={uid}, email={email})")

    choice = click.prompt("Select a user (번호 or username)")
    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(users):
            return users[idx - 1]
    else:
        return next((u for u in users if (u.get("username") or u.get("name")) == choice), None)
    return None


def select_roles(role_data: list):
    """Prompt the user to select one or more roles (번호 or 이름, comma-separated)"""
    if not role_data:
        click.secho("역할 목록이 비어있습니다.", fg="red")
        return []

    click.secho("📋 Available Roles:", fg="cyan")
    for idx, item in enumerate(role_data, 1):
        role = item.get("role", {}) if isinstance(item, dict) else {}
        proj = item.get("project", {}) if isinstance(item, dict) else {}
        rname = role.get("name") or item.get("role_name") or item.get("name") or "-"
        rdesc = role.get("description") or item.get("description") or "-"
        pname = proj.get("name") or "-"
        pcid = proj.get("client_id") or proj.get("id") or "-"
        click.echo(f"{idx}. {rname} (Project={pname} [{pcid}], desc={rdesc})")

    choice = click.prompt("Select roles (comma-separated: 번호 or 이름)")
    roles = [c.strip() for c in choice.split(",") if c.strip()]

    selected_roles = []
    for r in roles:
        selected = None
        if r.isdigit():
            idx = int(r)
            if 1 <= idx <= len(role_data):
                selected = role_data[idx - 1]
        else:
            # 이름으로 찾기
            selected = next((
                it for it in role_data
                if (it.get("role", {}) or {}).get("name") == r
                or it.get("role_name") == r
                or it.get("name") == r
            ), None)

        if not selected:
            click.secho(f"⚠️ 잘못된 role 입력: {r}", fg="yellow")
            continue
        selected_roles.append(selected)

    return selected_roles


def extract_list(container):
    """API 응답에서 리스트 파트를 최대한 유연하게 추출"""
    if isinstance(container, list):
        return container
    if isinstance(container, dict):
        for key in ["items", "content", "results", "data", "users", "roles"]:
            val = container.get(key)
            if isinstance(val, list):
                return val
    return []
