from typing import Any, override

from bafser import UserBase, UserKwargs, get_db_session, randstr
from sqlalchemy import BigInteger, String, func
from sqlalchemy.orm import Mapped, Session, mapped_column

from ..types import User


class TgUserBase(UserBase):
    __abstract__ = True
    _default_role = -1
    id_tg: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)
    is_bot: Mapped[bool] = mapped_column()
    first_name: Mapped[str] = mapped_column(String(128))
    last_name: Mapped[str] = mapped_column(String(128))
    username: Mapped[str] = mapped_column(String(128))
    language_code: Mapped[str] = mapped_column(String(16))

    @classmethod
    def new(cls, db_sess: Session, id_tg: int, is_bot: bool, first_name: str, last_name: str, username: str, language_code: str,
            *_: Any, **__: Any):
        fake_creator = UserBase.get_fake_system()
        return super().new(fake_creator, str(id_tg), randstr(8), username, [cls._default_role], db_sess=db_sess,
                           id_tg=id_tg, is_bot=is_bot, first_name=first_name, last_name=last_name, username=username, language_code=language_code)

    @classmethod
    @override
    def _new(cls, db_sess: Session, user_kwargs: UserKwargs, *,
             id_tg: int, is_bot: bool, first_name: str, last_name: str, username: str, language_code: str, **kwargs: Any):
        return cls(**user_kwargs,
                   id_tg=id_tg, is_bot=is_bot, first_name=first_name, last_name=last_name, username=username, language_code=language_code)

    @classmethod
    @override
    def create_admin(cls, db_sess: Session):
        return cls.new(db_sess, 0, False, "Админ", "", "admin", "en")

    def __repr__(self):
        return f"<User> [{self.id} {self.id_tg}] {self.username}"

    def get_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_username(self):
        if self.username != "":
            return self.username
        return self.get_name()

    def get_tagname(self):
        if self.username != "":
            return f"@{self.username}"
        return f"🥷 {self.get_name()}"

    @classmethod
    def new_from_data(cls, db_sess: Session, data: "User"):
        return cls.new(db_sess, data.id, data.is_bot, data.first_name, data.last_name, data.username, data.language_code)

    @classmethod
    def new_from_data2(cls, data: "User"):
        """Calls cls.new_from_data with db session from global context"""
        return cls.new_from_data(get_db_session(), data)

    @classmethod
    def get_by_id_tg(cls, db_sess: Session, id_tg: int, *, for_update: bool = False):
        return cls.query(db_sess, includeDeleted=True, for_update=for_update).filter(cls.id_tg == id_tg).first()

    @classmethod
    def get_by_id_tg2(cls, id_tg: int, *, for_update: bool = False):
        """Calls cls.get_by_id_tg with db session from global context"""
        return cls.get_by_id_tg(get_db_session(), id_tg, for_update=for_update)

    @classmethod
    def get_by_username(cls, db_sess: Session, username: str, *, for_update: bool = False):
        if username.startswith("@"):
            username = username[1:]
        return cls.query(db_sess, includeDeleted=True, for_update=for_update).filter(func.lower(cls.username) == username.lower()).first()

    @classmethod
    def get_by_username2(cls, username: str, *, for_update: bool = False):
        """Calls cls.get_by_username with db session from global context"""
        return cls.get_by_username(get_db_session(), username, for_update=for_update)
