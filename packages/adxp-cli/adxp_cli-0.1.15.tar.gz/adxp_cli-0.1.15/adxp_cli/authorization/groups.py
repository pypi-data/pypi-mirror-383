import click
import json
from adxp_cli.auth.service import get_credential
from adxp_cli.authorization.utils import select_user
from adxp_sdk.authorization.hub import AXAuthorizationHub


@click.group(name="group")
def group():
    """Manage Groups and User-Group mappings."""
    pass


# ====================================================================
# List Groups
# ====================================================================
@group.command(name="list")
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
@click.option("--json-output", is_flag=True, help="Output raw JSON")
def list_groups(page, size, json_output):
    """List Groups from the A.X Platform"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        groups = hub.list_groups(page=page, size=size)

        if json_output:
            click.echo(json.dumps(groups, indent=2))
        else:
            click.secho("👥 Group List:", fg="cyan")
            data = groups.get("data", [])
            if not data:
                click.secho("No groups found.", fg="yellow")
            for idx, item in enumerate(data, 1):
                gid = item.get("id")
                gname = item.get("name", "N/A")
                path = item.get("path", "")
                click.echo(f"{idx}. {gname} (ID={gid}, Path={path})")

        return groups

    except Exception as e:
        raise click.ClickException(f"❌ Failed to list groups: {e}")


# ====================================================================
# Create Group
# ====================================================================
@group.command(name="create")
@click.argument("name", required=False)
def create_group(name):
    """Create a new Group in the A.X Platform"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        # 인자 없으면 프롬프트로 입력
        if not name:
            name = click.prompt("Group name")

        group = hub.create_group(group_name=name)

        click.secho(
            f"✅ Group Created! ID={group.get('id')} Name={group.get('name', name)}",
            fg="green",
        )

    except Exception as e:
        raise click.ClickException(f"❌ Failed to create group: {e}")



# ====================================================================
# Update Group
# ====================================================================
@group.command(name="update")
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
@click.argument("name", required=False)
def update_group(page, size, name):
    """Update an existing Group in the A.X Platform"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        selected = None

        if name:
            # name 직접 입력 → 전체 페이지 탐색
            search_page = 1
            while True:
                groups = hub.list_groups(page=search_page, size=size)
                data = groups.get("data", [])
                if not data:
                    break
                for item in data:
                    if item.get("name") == name:
                        selected = item
                        break
                if selected:
                    break
                search_page += 1

            if not selected:
                click.secho(f"❌ 그룹 '{name}' 를 찾을 수 없습니다.", fg="red")
                return
        else:
            groups = hub.list_groups(page=page, size=size)
            data = groups.get("data", [])
            if not data:
                click.secho("⚠️ No groups found.", fg="yellow")
                return

            click.secho("👥 Group List:", fg="cyan")
            for idx, item in enumerate(data, 1):
                gid = item.get("id")
                gname = item.get("name", "N/A")
                click.echo(f"{idx}. {gname} (ID={gid})")

            choice = click.prompt("수정할 그룹 선택 (번호 또는 이름)")
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(data):
                    selected = data[idx - 1]
            else:
                for item in data:
                    if item.get("name") == choice:
                        selected = item
                        break

            if not selected:
                click.secho("❌ 잘못된 입력입니다. 다시 시도해주세요.", fg="red")
                return

        group_id = selected.get("id")
        current_name = selected.get("name", "")

        new_name = click.prompt("Group name", default=current_name, show_default=True)
        
        group = hub.update_group(group_id=group_id, group_name=new_name)

        click.secho(
            f"✅ Group Updated! ID={group.get('id', group_id)} Name={group.get('name', new_name)}",
            fg="green",
        )

    except Exception as e:
        raise click.ClickException(f"❌ Failed to update group: {e}")


# ====================================================================
# Delete Group (리소스 자체 삭제)
# ====================================================================
@group.command(name="delete")
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
@click.argument("name", required=False)
def delete_group(page, size, name):
    """Delete a Group from the A.X Platform"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        selected = None

        if name:
            # name 직접 입력 → 전체 페이지 탐색
            search_page = 1
            while True:
                groups = hub.list_groups(page=search_page, size=size)
                data = groups.get("data", [])
                if not data:
                    break
                for item in data:
                    if item.get("name") == name:
                        selected = item
                        break
                if selected:
                    break
                search_page += 1

            if not selected:
                click.secho(f"❌ 그룹 '{name}' 를 찾을 수 없습니다.", fg="red")
                return
        else:
            groups = hub.list_groups(page=page, size=size)
            data = groups.get("data", [])
            if not data:
                click.secho("⚠️ No groups found.", fg="yellow")
                return

            click.secho("👥 Group List:", fg="cyan")
            for idx, item in enumerate(data, 1):
                gid = item.get("id")
                gname = item.get("name", "N/A")
                click.echo(f"{idx}. {gname} (ID={gid})")

            choice = click.prompt("삭제할 그룹 선택 (번호 또는 이름)")
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(data):
                    selected = data[idx - 1]
            else:
                for item in data:
                    if item.get("name") == choice:
                        selected = item
                        break

            if not selected:
                click.secho("❌ 잘못된 입력입니다. 다시 시도해주세요.", fg="red")
                return

        group_id = selected.get("id")
        group_name = selected.get("name")

        confirm = click.confirm(
            f"정말로 그룹 '{group_name}' (ID={group_id}) 를 삭제하시겠습니까?",
            default=False,
        )
        if not confirm:
            click.secho("🚫 삭제 취소됨", fg="yellow")
            return

        result = hub.delete_group(group_id=group_id)

        click.secho(
            f"🗑️ Group Deleted! ID={result.get('id', group_id)} Name={group_name}",
            fg="red",
        )

    except Exception as e:
        raise click.ClickException(f"❌ Failed to delete group: {e}")


# ====================================================================
# User-Group Mappings
# ====================================================================

@group.command(name="assigned")
@click.argument("username", required=False)
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
def list_assigned_groups(username, page, size):
    """List groups currently assigned to a user"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        if not username:
            users = hub.list_users(page=1, size=50).get("data", [])
            selected_user = select_user(users)
            if not selected_user:
                return
        else:
            selected_user = None
            search_page = 1
            while True:
                user_page = hub.list_users(page=search_page, size=50).get("data", [])
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

        assigned = hub.list_user_assigned_groups(user_id=user_id, page=page, size=size)
        group_data = assigned.get("data", [])

        if not group_data:
            click.secho("⚠️ No groups assigned.", fg="yellow")
            return

        click.secho(f"📋 Groups assigned to '{username}':", fg="cyan")
        for idx, g in enumerate(group_data, 1):
            gname = g.get("name") or "-"
            gid = g.get("id") or "-"
            click.echo(f"{idx}. {gname} (ID={gid})")

    except Exception as e:
        raise click.ClickException(f"❌ Failed to list assigned groups: {e}")


@group.command(name="available")
@click.argument("username", required=False)
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
def list_available_groups(username, page, size):
    """List groups available for assignment to a user"""
    try:
        headers, config = get_credential()
        hub = AXAuthorizationHub(headers=headers, base_url=config.base_url)

        if not username:
            users = hub.list_users(page=1, size=50).get("data", [])
            selected_user = select_user(users)
            if not selected_user:
                return
        else:
            selected_user = None
            search_page = 1
            while True:
                user_page = hub.list_users(page=search_page, size=50).get("data", [])
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

        available = hub.list_user_available_groups(user_id=user_id, page=page, size=size)
        group_data = available.get("data", [])

        if not group_data:
            click.secho("⚠️ No available groups.", fg="yellow")
            return

        click.secho(f"📋 Groups available for '{username}':", fg="cyan")
        for idx, g in enumerate(group_data, 1):
            gname = g.get("name") or "-"
            gid = g.get("id") or "-"
            click.echo(f"{idx}. {gname} (ID={gid})")

    except Exception as e:
        raise click.ClickException(f"❌ Failed to list available groups: {e}")


@group.command(name="assign")
@click.argument("username", required=False)
@click.option("--group-id", multiple=True, help="Group IDs to assign (can specify multiple)")
@click.option("--page", default=1, help="Page number for groups")
@click.option("--size", default=10, help="Page size for groups")
def assign_group(username, group_id, page, size):
    """Assign one or more groups to a user"""
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
                user_page = hub.list_users(page=search_page, size=50).get("data", [])
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

        # 그룹 선택
        selected_groups = []
        if not group_id:
            available = hub.list_user_available_groups(user_id=user_id, page=page, size=size)
            group_data = available.get("data", [])

            if not group_data:
                click.secho("⚠️ No available groups.", fg="yellow")
                return

            click.secho("📋 Available Groups:", fg="cyan")
            for idx, g in enumerate(group_data, 1):
                gname = g.get("name") or "-"
                gid = g.get("id") or "-"
                click.echo(f"{idx}. {gname} (ID={gid})")

            choice = click.prompt("Select groups (comma-separated: 번호 or ID)")
            group_id = [c.strip() for c in choice.split(",") if c.strip()]

            for g in group_id:
                selected = None
                if g.isdigit():
                    idx = int(g)
                    if 1 <= idx <= len(group_data):
                        selected = group_data[idx - 1]
                else:
                    selected = next((item for item in group_data if item.get("id") == g or item.get("name") == g), None)

                if not selected:
                    click.secho(f"⚠️ 잘못된 그룹 입력: {g}", fg="yellow")
                    continue
                selected_groups.append(selected)
        else:
            for gid in group_id:
                selected_groups.append({"id": gid})

        # API 호출 (N번)
        for g in selected_groups:
            gid = g.get("id")
            hub.assign_group_to_user(user_id=user_id, group_id=gid)

        click.secho(
            f"✅ Assigned {len(selected_groups)} group(s) to user '{username}'",
            fg="green",
        )

    except Exception as e:
        raise click.ClickException(f"❌ Failed to assign group: {e}")


@group.command(name="unassign")
@click.argument("username", required=False)
@click.option("--group-id", multiple=True, help="Group IDs to unassign (can specify multiple)")
@click.option("--page", default=1, help="Page number for groups")
@click.option("--size", default=10, help="Page size for groups")
def unassign_group(username, group_id, page, size):
    """Unassign (remove) one or more groups from a user"""
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
                user_page = hub.list_users(page=search_page, size=50).get("data", [])
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

        # 그룹 선택
        selected_groups = []
        if not group_id:
            assigned = hub.list_user_assigned_groups(user_id=user_id, page=page, size=size)
            group_data = assigned.get("data", [])

            if not group_data:
                click.secho("⚠️ No assigned groups.", fg="yellow")
                return

            click.secho("📋 Assigned Groups:", fg="cyan")
            for idx, g in enumerate(group_data, 1):
                gname = g.get("name") or "-"
                gid = g.get("id") or "-"
                click.echo(f"{idx}. {gname} (ID={gid})")

            choice = click.prompt("Select groups to unassign (comma-separated: 번호 or ID)")
            group_id = [c.strip() for c in choice.split(",") if c.strip()]

            for g in group_id:
                selected = None
                if g.isdigit():
                    idx = int(g)
                    if 1 <= idx <= len(group_data):
                        selected = group_data[idx - 1]
                else:
                    selected = next((item for item in group_data if item.get("id") == g or item.get("name") == g), None)

                if not selected:
                    click.secho(f"⚠️ 잘못된 그룹 입력: {g}", fg="yellow")
                    continue
                selected_groups.append(selected)
        else:
            for gid in group_id:
                selected_groups.append({"id": gid})

        # API 호출 (N번)
        for g in selected_groups:
            gid = g.get("id")
            hub.delete_group_from_user(user_id=user_id, group_id=gid)

        click.secho(
            f"🗑️ Unassigned {len(selected_groups)} group(s) from user '{username}'",
            fg="yellow",
        )

    except Exception as e:
        raise click.ClickException(f"❌ Failed to unassign group: {e}")

