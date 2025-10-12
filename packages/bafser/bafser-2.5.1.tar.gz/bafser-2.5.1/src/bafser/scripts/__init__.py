from .add_user_role import add_user_role
from .add_user import add_user
from .alembic import init as _alembic_init, revision as _alembic_revision, upgrade as _alembic_upgrade
from .change_user_password import change_user_password
from .remove_user_role import remove_user_role


def alembic_init():
    _alembic_init([])


def alembic_revision(name: str | None = None):
    _alembic_revision([] if name is None else [name])


def alembic_upgrade():
    _alembic_upgrade([])


__all__ = [
    "add_user_role",
    "add_user",
    "alembic_init", "alembic_revision", "alembic_upgrade",
    "change_user_password",
    "remove_user_role",
]
