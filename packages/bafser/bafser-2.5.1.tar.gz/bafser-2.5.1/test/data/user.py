from test.data import Roles, Tables
from typing import TYPE_CHECKING, Any, List, Optional, override

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from bafser import UserBase, UserKwargs

if TYPE_CHECKING:
    from test.data.apple import Apple
    from test.data.img import Img


class User(UserBase):
    avatarId: Mapped[Optional[int]] = mapped_column(ForeignKey(f"{Tables.Image}.id"), init=False)
    balance: Mapped[int]

    avatar: Mapped["Img"] = relationship(init=False, foreign_keys=f"{Tables.User}.avatarId")
    apples: Mapped[List["Apple"]] = relationship(back_populates="owner", default_factory=list)

    def __repr__(self):
        return f"<{self.__class__.__name__}> [{self.id}] {self.login}"

    @classmethod
    @override
    def new(cls, creator: UserBase, login: str, password: str, name: str, roles: list[int], balance: int, *, db_sess: Session | None = None):
        return super().new(creator, login, password, name, roles, db_sess=db_sess, balance=balance)

    @classmethod
    @override
    def _new(cls, db_sess: Session, user_kwargs: UserKwargs, *, balance: int, **kwargs: Any):
        return User(**user_kwargs, balance=balance)

    @classmethod
    @override
    def create_admin(cls, db_sess: Session):
        fake_creator = User.get_fake_system()
        return User.new(fake_creator, "admin", "admin", "Admin", [Roles.admin], 0, db_sess=db_sess)
