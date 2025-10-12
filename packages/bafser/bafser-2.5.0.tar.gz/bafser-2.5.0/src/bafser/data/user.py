from typing import Any, List, Type, TypedDict, TypeVar

from flask import abort, g
from flask_jwt_extended import get_jwt_identity, unset_jwt_cookies, verify_jwt_in_request  # type: ignore
from sqlalchemy import String
from sqlalchemy.orm import Mapped, Session, declared_attr, lazyload, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from .. import ObjMixin, SqlAlchemyBase, UserRole, listfind
from ..utils import get_datetime_now
from ._roles import RolesBase
from ._tables import TablesBase

T = TypeVar("T", bound="UserBase")
_User: "Type[UserBase] | None" = None
TFieldName = str
TValue = Any


class UserKwargs(TypedDict):
    login: str
    name: str


def get_user_table():
    if _User is None:
        raise Exception("[bafser] No class inherited from UserBase")
    return _User


class UserBase(ObjMixin, SqlAlchemyBase):
    __tablename__ = TablesBase.User
    __abstract__ = True
    __fields_hidden_in_log__ = ["password"]

    login: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    password: Mapped[str] = mapped_column(String(256), init=False)
    name: Mapped[str] = mapped_column(String(64))

    @declared_attr
    def roles(self) -> Mapped[List[UserRole]]:
        return relationship(UserRole, lazy="joined", init=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}> [{self.id}] {self.login}"

    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        super().__init_subclass__(*args, **kwargs)
        global _User
        _User = cls

    @classmethod
    def new(cls, creator: "UserBase", login: str, password: str, name: str, roles: list[int], *_: Any, db_sess: Session | None = None, **kwargs: Any):  # noqa: E501
        from .. import Log
        db_sess = db_sess if db_sess else creator.db_sess
        user = cls._new(db_sess, {"login": login, "name": name}, **kwargs)
        user.set_password(password)
        db_sess.add(user)

        now = get_datetime_now()
        Log.added(user, creator, None, now, db_sess=db_sess)

        for roleId in roles:
            UserRole.new(creator, user.id, roleId, now=now, commit=False, db_sess=db_sess)

        db_sess.commit()

        return user

    @classmethod
    def _new(cls: Type[T], db_sess: Session, user_kwargs: UserKwargs, **kwargs: Any) -> T:
        return cls(**user_kwargs)

    @classmethod
    def get_lazy(cls, db_sess: Session, id: int, includeDeleted: bool = False, *, for_update: bool = False):
        return cls.query(db_sess, includeDeleted, for_update=for_update).filter(cls.id == id).options(lazyload(cls.roles)).first()

    @classmethod
    def get_by_login(cls, db_sess: Session, login: str, includeDeleted: bool = False, *, for_update: bool = False):
        return cls.query(db_sess, includeDeleted, for_update=for_update).filter(cls.login == login).first()

    @classmethod
    def get_current(cls: Type[T], *, lazyload: bool = False, for_update: bool = False) -> T | None:
        from .. import get_db_session, get_user_by_jwt_identity
        try:
            if "user" in g:
                return g.user
            verify_jwt_in_request()
            db_sess = get_db_session()
            user = get_user_by_jwt_identity(db_sess, get_jwt_identity(), lazyload=lazyload, for_update=for_update)
            g.user = user
            return user  # type: ignore
        except Exception:
            try:
                g.user = None
            except Exception:
                pass
            return None

    @classmethod
    @property
    def current(cls):  # pyright: ignore[reportDeprecated]
        from .. import response_msg
        user = cls.get_current()
        if user is not None:
            return user

        response = response_msg("The JWT has expired", 401)
        unset_jwt_cookies(response)
        abort(response)

    @classmethod
    def create_admin(cls, db_sess: Session):
        fake_creator = UserBase.get_fake_system()
        return cls.new(fake_creator, "admin", "admin", "Admin", [RolesBase.admin], db_sess=db_sess)

    @staticmethod
    def _create_admin(db_sess: Session):
        User = get_user_table()
        admin = User.get_admin(db_sess)
        if admin:
            return admin
        return User.create_admin(db_sess)

    @classmethod
    def get_admin(cls, db_sess: Session):
        return cls.query(db_sess).join(UserRole).filter(UserRole.roleId == RolesBase.admin).options(lazyload(cls.roles)).first()

    def is_admin(self):
        return self.has_role(RolesBase.admin)

    @staticmethod
    def get_fake_system():
        u = UserBase(name="System", login="system")
        u.id = 1
        return u

    @classmethod
    def all_of_role(cls, db_sess: Session, role: int, includeDeleted: bool = False, *, for_update: bool = False):
        return cls.query(db_sess, includeDeleted, for_update=for_update).join(UserRole).filter(UserRole.roleId == role).all()

    def update_password(self, actor: "UserBase", password: str):
        from .. import Log
        self.set_password(password)
        Log.updated(self, actor)

    def update_name(self, actor: "UserBase", name: str):
        from .. import Log
        self.name = name
        Log.updated(self, actor)

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password, password)

    def check_permission(self, operation: tuple[str, str]):
        return operation[0] in self.get_operations()

    def add_role(self, actor: "UserBase", roleId: int):
        if roleId in self.get_roles_ids():
            return False
        UserRole.new(actor, self.id, roleId)
        return True

    def remove_role(self, actor: "UserBase", roleId: int):
        user_role = listfind(self.roles, lambda r: r.roleId == roleId)
        if not user_role:
            return False
        user_role.delete(actor)
        return True

    def get_roles(self) -> list[tuple[int, str]]:
        return [(r.roleId, r.role.name) for r in self.roles]

    def get_roles_ids(self):
        return [v[0] for v in self.get_roles()]

    def get_roles_names(self):
        return [v[1] for v in self.get_roles()]

    def has_role(self, roleId: int):
        return roleId in self.get_roles_ids()

    def get_operations(self) -> list[str]:
        return [v.operationId for r in self.roles for v in r.role.permissions]

    def get_dict(self) -> "UserDict":
        return {
            "id": self.id,
            "name": self.name,
            "login": self.login,
            "roles": self.get_roles_names(),
            "operations": self.get_operations(),
        }

    def get_dict_full(self) -> "UserDictFull":
        return {
            "id": self.id,
            "deleted": self.deleted,
            "name": self.name,
            "login": self.login,
            "roles": self.get_roles(),
            "operations": self.get_operations(),
        }


class UserDict(TypedDict):
    id: int
    name: str
    login: str
    roles: list[str]
    operations: list[str]


class UserDictFull(TypedDict):
    id: int
    deleted: bool
    name: str
    login: str
    roles: list[tuple[int, str]]
    operations: list[str]
