from datetime import datetime, timezone
from sqlalchemy import Column, Boolean, Enum
from .base import Base
from utils.enums import UserRoles
from sqlalchemy.orm import (
    mapped_column,
    relationship,
    Mapped
)
from sqlalchemy import (
    String,
    ForeignKey,
    DateTime
)


class BaseMixin:
    createdAt = Column(DateTime, default=datetime.now(tz=timezone.utc))
    modifiedAt = Column(DateTime, default=datetime.now(tz=timezone.utc), onupdate=datetime.now(timezone.utc))


class User(Base, BaseMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(), unique=True)
    password: Mapped[str] = mapped_column(String())
    isActive = Column(Boolean, nullable=False, default=False)
    isSuperUser = Column(Boolean, nullable=False, default=False)

    roles: Mapped[list['Role']] = relationship(
        secondary="role_by_user",
        back_populates="users"
    )

    roles_user: Mapped[list['RoleByUser']] = relationship(
        lazy='noload',
        back_populates="user"
    )


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(60))

    users: Mapped[list[User]] = relationship(
        secondary="role_by_user",
        back_populates="roles"
    )

    users_role: Mapped[list['RoleByUser']] = relationship(
        lazy='noload',
        back_populates='role'
    )


class RoleByUser(Base):
    __tablename__ = 'role_by_user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    id_role: Mapped[int] = mapped_column(ForeignKey('roles.id'))
    id_user: Mapped[int] = mapped_column(ForeignKey('users.id'))

    role: Mapped[Role] = relationship(back_populates='users_role')
    user: Mapped[User] = relationship(back_populates='roles_user')

    operator: Mapped['Operator'] = relationship(lazy='noload', back_populates="role_user")
    forklift: Mapped['Forklift'] = relationship(lazy='noload', back_populates="role_user")


class Operator(Base):
    __tablename__ = 'operators'

    id: Mapped[int] = mapped_column(ForeignKey('role_by_user.id'), primary_key=True, autoincrement=False)
    machine: Mapped[str] = mapped_column(String())
    area: Mapped[str] = mapped_column(String())

    role_user: Mapped[RoleByUser] = relationship(lazy='noload', back_populates="operator")


class Forklift(Base):
    __tablename__ = 'forklifts'

    id: Mapped[int] = mapped_column(ForeignKey('role_by_user.id'), primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String())

    role_user: Mapped[RoleByUser] = relationship(lazy='noload', back_populates="forklift")


class Admin(Base):
    __tablename__ = 'forklifts'

    id: Mapped[int] = mapped_column(ForeignKey('role_by_user.id'), primary_key=True, autoincrement=False)
    firstName: Mapped[str] = mapped_column(String())
    lastName: Mapped[str] = mapped_column(String())

    role_user: Mapped[RoleByUser] = relationship(lazy='noload', back_populates="forklift")


class Material(Base):
    __tablename__ = 'materials'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(60))
    unit: Mapped[str] = mapped_column(String(60))
    color: Mapped[int] = mapped_column(String(60))
    imagen: Mapped[str] = mapped_column(String(60))
