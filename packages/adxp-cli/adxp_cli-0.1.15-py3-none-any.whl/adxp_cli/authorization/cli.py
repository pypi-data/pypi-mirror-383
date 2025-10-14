import click
from .projects import project
from .users import user
from .groups import group

@click.group()
def authorization():
    """Command-line interface for Authorization (Projects, Users, Groups)."""
    pass

# 하위 그룹 등록
authorization.add_command(project)
authorization.add_command(user)
authorization.add_command(group)

__all__ = ["authorization"]
