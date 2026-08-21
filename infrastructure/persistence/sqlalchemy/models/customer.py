from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    Text,
    func,
    text
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from infrastructure.persistence.sqlalchemy.base import (
    Base
)


class CustomerGroupModel(Base):

    __tablename__ = "customer_groups"

    customer_group_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        server_default=func.now(),
        nullable=False
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id"
        ),
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id"
        ),
        nullable=True
    )

    customers: Mapped[
        list[CustomerModel]
    ] = relationship(
        back_populates="group"
    )


class CustomerModel(Base):

    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    customer_group_id: Mapped[
        int | None
    ] = mapped_column(
        ForeignKey(
            "customer_groups.customer_group_id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    person_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    document: Mapped[str] = mapped_column(
        String(14),
        nullable=False,
        unique=True
    )

    legal_name: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    trade_name: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    state_registration: Mapped[
        str | None
    ] = mapped_column(
        String(50),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    general_observation: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id"
        ),
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id"
        ),
        nullable=True
    )

    group: Mapped[
        CustomerGroupModel | None
    ] = relationship(
        back_populates="customers"
    )

    contacts: Mapped[
        list[CustomerContactModel]
    ] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
        order_by="CustomerContactModel.customer_contact_id"
    )

    addresses: Mapped[
        list[CustomerAddressModel]
    ] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
        order_by="CustomerAddressModel.customer_address_id"
    )

    operational_locations: Mapped[
        list[CustomerOperationalLocationModel]
    ] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
        order_by=(
            "CustomerOperationalLocationModel."
            "operational_location_id"
        )
    )


class CustomerContactModel(Base):

    __tablename__ = "customer_contacts"

    __table_args__ = (
        Index(
            "uq_customer_contacts_customer_primary",
            "customer_id",
            unique=True,
            postgresql_where=text(
                "is_primary IS TRUE"
            )
        ),
    )

    customer_contact_id: Mapped[
        int
    ] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "customers.customer_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    name: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    phone: Mapped[
        str | None
    ] = mapped_column(
        String(50),
        nullable=True
    )

    whatsapp: Mapped[
        str | None
    ] = mapped_column(
        String(50),
        nullable=True
    )

    email: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    position_or_department: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        server_default=func.now(),
        nullable=False
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id"
        ),
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id"
        ),
        nullable=True
    )

    customer: Mapped[
        CustomerModel
    ] = relationship(
        back_populates="contacts"
    )


class CustomerAddressModel(Base):

    __tablename__ = "customer_addresses"

    __table_args__ = (
        Index(
            "uq_customer_addresses_customer_primary",
            "customer_id",
            unique=True,
            postgresql_where=text(
                "is_primary IS TRUE"
            )
        ),
    )

    customer_address_id: Mapped[
        int
    ] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "customers.customer_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    address_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    postal_code: Mapped[
        str | None
    ] = mapped_column(
        String(20),
        nullable=True
    )

    street: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    number: Mapped[
        str | None
    ] = mapped_column(
        String(50),
        nullable=True
    )

    complement: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    district: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    city: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    state: Mapped[
        str | None
    ] = mapped_column(
        String(2),
        nullable=True
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        server_default=func.now(),
        nullable=False
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id"
        ),
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id"
        ),
        nullable=True
    )

    customer: Mapped[
        CustomerModel
    ] = relationship(
        back_populates="addresses"
    )


class CustomerOperationalLocationModel(Base):

    __tablename__ = (
        "customer_operational_locations"
    )

    operational_location_id: Mapped[
        int
    ] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "customers.customer_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    postal_code: Mapped[
        str | None
    ] = mapped_column(
        String(20),
        nullable=True
    )

    street: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    number: Mapped[
        str | None
    ] = mapped_column(
        String(50),
        nullable=True
    )

    complement: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    district: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    city: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    state: Mapped[
        str | None
    ] = mapped_column(
        String(2),
        nullable=True
    )

    observation: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        server_default=func.now(),
        nullable=False
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id"
        ),
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id"
        ),
        nullable=True
    )

    customer: Mapped[
        CustomerModel
    ] = relationship(
        back_populates="operational_locations"
    )