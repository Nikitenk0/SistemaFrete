from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
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


class DriverModel(Base):

    __tablename__ = "drivers"

    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_drivers_status"
        ),
        CheckConstraint(
            "char_length(cpf) = 11",
            name="ck_drivers_cpf_length"
        ),
    )

    driver_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    cpf: Mapped[str] = mapped_column(
        String(11),
        nullable=False,
        unique=True
    )

    rg: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    birth_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    cnh_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    cnh_category: Mapped[str] = mapped_column(
        String(5),
        nullable=False
    )

    cnh_expiration_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    contacts: Mapped[
        list[DriverContactModel]
    ] = relationship(
        back_populates="driver",
        cascade="all, delete-orphan",
        order_by="DriverContactModel.driver_contact_id"
    )

    addresses: Mapped[
        list[DriverAddressModel]
    ] = relationship(
        back_populates="driver",
        cascade="all, delete-orphan",
        order_by="DriverAddressModel.driver_address_id"
    )

    bank_accounts: Mapped[
        list[DriverBankAccountModel]
    ] = relationship(
        back_populates="driver",
        cascade="all, delete-orphan",
        order_by="DriverBankAccountModel.driver_bank_account_id"
    )


class DriverContactModel(Base):

    __tablename__ = "driver_contacts"

    __table_args__ = (
        Index(
            "uq_driver_contacts_driver_primary",
            "driver_id",
            unique=True,
            postgresql_where=text(
                "is_primary IS TRUE"
            )
        ),
    )

    driver_contact_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    driver_id: Mapped[int] = mapped_column(
        ForeignKey(
            "drivers.driver_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    secondary_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    driver: Mapped[
        DriverModel
    ] = relationship(
        back_populates="contacts"
    )


class DriverAddressModel(Base):

    __tablename__ = "driver_addresses"

    __table_args__ = (
        Index(
            "uq_driver_addresses_driver_primary",
            "driver_id",
            unique=True,
            postgresql_where=text(
                "is_primary IS TRUE"
            )
        ),
        CheckConstraint(
            "address_type IN ('RESIDENTIAL', 'OTHER')",
            name="ck_driver_addresses_address_type"
        ),
        CheckConstraint(
            "char_length(postal_code) = 8",
            name="ck_driver_addresses_postal_code_length"
        ),
    )

    driver_address_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    driver_id: Mapped[int] = mapped_column(
        ForeignKey(
            "drivers.driver_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    address_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    postal_code: Mapped[str] = mapped_column(
        String(8),
        nullable=False
    )

    street: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    number: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    complement: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    district: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    city: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    state: Mapped[str] = mapped_column(
        String(2),
        nullable=False
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    driver: Mapped[
        DriverModel
    ] = relationship(
        back_populates="addresses"
    )


class DriverBankAccountModel(Base):

    __tablename__ = "driver_bank_accounts"

    __table_args__ = (
        Index(
            "uq_driver_bank_accounts_driver_primary",
            "driver_id",
            unique=True,
            postgresql_where=text(
                "is_primary IS TRUE"
            )
        ),
        CheckConstraint(
            "account_type IN ('CHECKING', 'SAVINGS', 'PAYMENT')",
            name="ck_driver_bank_accounts_account_type"
        ),
        CheckConstraint(
            "pix_key_type IS NULL OR pix_key_type IN "
            "('CPF', 'EMAIL', 'PHONE', 'RANDOM')",
            name="ck_driver_bank_accounts_pix_key_type"
        ),
        CheckConstraint(
            "(pix_key_type IS NULL AND pix_key IS NULL) OR "
            "(pix_key_type IS NOT NULL AND pix_key IS NOT NULL)",
            name="ck_driver_bank_accounts_pix_pair"
        ),
        CheckConstraint(
            "char_length(bank_code) = 3",
            name="ck_driver_bank_accounts_bank_code_length"
        ),
    )

    driver_bank_account_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    driver_id: Mapped[int] = mapped_column(
        ForeignKey(
            "drivers.driver_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    bank_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False
    )

    agency: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    account: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    account_digit: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    account_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    pix_key_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    pix_key: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    driver: Mapped[
        DriverModel
    ] = relationship(
        back_populates="bank_accounts"
    )
