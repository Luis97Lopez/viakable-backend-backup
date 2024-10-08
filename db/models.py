from datetime import datetime, timezone
from sqlalchemy import Column, Boolean
from .base import Base
from typing import Optional
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
        back_populates="users",
        cascade='all, delete',
        viewonly=True
    )

    roles_user: Mapped[list['RoleByUser']] = relationship(
        lazy='noload',
        cascade='all, delete',
        back_populates="user"
    )


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[str] = mapped_column(primary_key=True)

    users: Mapped[list[User]] = relationship(
        secondary="role_by_user",
        back_populates="roles",
        viewonly=True
    )

    users_role: Mapped[list['RoleByUser']] = relationship(
        lazy='noload',
        back_populates='role'
    )


class RoleByUser(Base):
    __tablename__ = 'role_by_user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    id_role: Mapped[str] = mapped_column(ForeignKey('roles.id'))
    id_user: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))

    role: Mapped[Role] = relationship(back_populates='users_role')
    user: Mapped[User] = relationship(back_populates='roles_user')

    operator: Mapped['Operator'] = relationship(lazy='noload', back_populates="role_user", cascade='all, delete')
    forklift: Mapped['Forklift'] = relationship(lazy='noload', back_populates="role_user",  cascade='all, delete')
    admin: Mapped['Admin'] = relationship(lazy='noload', back_populates="role_user",  cascade='all, delete')


class Operator(Base):
    __tablename__ = 'operators'

    id: Mapped[int] = mapped_column(ForeignKey('role_by_user.id', ondelete="CASCADE"), primary_key=True,
                                    autoincrement=False)
    machine: Mapped[str] = mapped_column(String())
    area: Mapped[str] = mapped_column(String())

    role_user: Mapped[RoleByUser] = relationship(lazy='joined', back_populates="operator")


class Forklift(Base):
    __tablename__ = 'forklifts'

    id: Mapped[int] = mapped_column(ForeignKey('role_by_user.id', ondelete="CASCADE"), primary_key=True,
                                    autoincrement=False)
    name: Mapped[str] = mapped_column(String())

    role_user: Mapped[RoleByUser] = relationship(lazy='joined', back_populates="forklift")


class Admin(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(ForeignKey('role_by_user.id', ondelete="CASCADE"), primary_key=True,
                                    autoincrement=False)
    firstName: Mapped[str] = mapped_column(String())
    lastName: Mapped[str] = mapped_column(String())

    role_user: Mapped[RoleByUser] = relationship(lazy='joined', back_populates="admin")


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_operator: Mapped[int] = mapped_column(ForeignKey('users.id'))
    id_forklift: Mapped[int] = mapped_column(ForeignKey('users.id'))

    creation_datetime: Mapped[datetime] = mapped_column(DateTime())
    estimate_datetime: Mapped[datetime] = mapped_column(DateTime())
    order_datetime: Mapped[Optional[datetime]] = mapped_column(DateTime(), nullable=True)
    state: Mapped[str] = mapped_column(String(60))
    canceled: Mapped[bool] = mapped_column(default=False)

    materials: Mapped[list['Material']] = relationship(
        secondary="material_by_order",
        back_populates="orders",
        viewonly=True
    )

    materials_order: Mapped[list['MaterialByOrder']] = relationship(
        back_populates="order"
    )

    operator: Mapped[User] = relationship(
        lazy='joined',
        primaryjoin='Order.id_operator == User.id'
    )

    forklift: Mapped[User] = relationship(
        lazy='joined',
        primaryjoin='Order.id_forklift == User.id'
    )


class Material(Base):
    __tablename__ = 'materials'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(60))
    unit: Mapped[str] = mapped_column(String(60))
    color: Mapped[Optional[str]] = mapped_column(String(60))
    image: Mapped[Optional[str]] = mapped_column(String(60))

    orders: Mapped[list[Order]] = relationship(
        secondary="material_by_order",
        back_populates="materials",
        viewonly=True
    )

    materials_order: Mapped[list['MaterialByOrder']] = relationship(
        back_populates="material",
        lazy="noload"
    )


class MaterialByOrder(Base):
    __tablename__ = 'material_by_order'

    id_material: Mapped[int] = mapped_column(ForeignKey('materials.id'), primary_key=True)
    id_order: Mapped[int] = mapped_column(ForeignKey('orders.id'), primary_key=True)
    quantity: Mapped[int] = mapped_column()

    material: Mapped[Material] = relationship(back_populates='materials_order', innerjoin=True)
    order: Mapped[Order] = relationship(back_populates='materials_order', innerjoin=True)
