from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from infrastructure.persistence.sqlalchemy.base import (
    Base
)


class AdministrativeCostPolicyModel(Base):

    __tablename__ = (
        "administrative_cost_policies"
    )
    __table_args__ = (
        CheckConstraint(
            "rate >= 0 AND rate < 1",
            name=(
                "ck_administrative_cost_policies_"
                "rate"
            )
        ),
        CheckConstraint(
            "minimum_value >= 0",
            name=(
                "ck_administrative_cost_policies_"
                "minimum_value"
            )
        ),
        CheckConstraint(
            (
                "effective_to IS NULL "
                "OR effective_to > effective_from"
            ),
            name=(
                "ck_administrative_cost_policies_"
                "effective_period"
            )
        ),
    )
    administrative_cost_policy_id: Mapped[
        int
    ] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    tracking_required: Mapped[
        bool
    ] = mapped_column(
        Boolean,
        nullable=False,
        index=True
    )

    rate: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    minimum_value: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    effective_to: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    created_by: Mapped[
        int | None
    ] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )


class MarginTableModel(Base):

    __tablename__ = "margin_tables"
    __table_args__ = (
        CheckConstraint(
            (
                "effective_to IS NULL "
                "OR effective_to > effective_from"
            ),
            name=(
                "ck_margin_tables_effective_period"
            )
        ),
    )

    margin_table_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    effective_to: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    created_by: Mapped[
        int | None
    ] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    bands: Mapped[
        list["MarginBandModel"]
    ] = relationship(
        back_populates="margin_table",
        cascade="all, delete-orphan",
        order_by="MarginBandModel.position"
    )


class MarginBandModel(Base):

    __tablename__ = "margin_bands"

    __table_args__ = (
        UniqueConstraint(
            "margin_table_id",
            "position",
            name=(
                "uq_margin_bands_"
                "margin_table_id_position"
            )
        ),
        CheckConstraint(
            "position >= 1",
            name="ck_margin_bands_position"
        ),
        CheckConstraint(
            "rate >= 0 AND rate < 1",
            name="ck_margin_bands_rate"
        ),
        CheckConstraint(
            (
                "lower_bound_exclusive IS NULL "
                "OR lower_bound_exclusive >= 0"
            ),
            name=(
                "ck_margin_bands_lower_bound"
            )
        ),
        CheckConstraint(
            (
                "upper_bound_inclusive IS NULL "
                "OR upper_bound_inclusive >= 0"
            ),
            name=(
                "ck_margin_bands_upper_bound"
            )
        ),
        CheckConstraint(
            (
                "lower_bound_exclusive IS NULL "
                "OR upper_bound_inclusive IS NULL "
                "OR upper_bound_inclusive "
                "> lower_bound_exclusive"
            ),
            name=(
                "ck_margin_bands_bounds"
            )
        ),
    )

    margin_band_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    margin_table_id: Mapped[int] = mapped_column(
        ForeignKey(
            "margin_tables.margin_table_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    position: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    lower_bound_exclusive: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    upper_bound_inclusive: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    rate: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    margin_table: Mapped[
        MarginTableModel
    ] = relationship(
        back_populates="bands"
    )


class TaxPolicyModel(Base):

    __tablename__ = "tax_policies"

    __table_args__ = (
        CheckConstraint(
            "rate >= 0 AND rate < 1",
            name="ck_tax_policies_rate"
        ),
        CheckConstraint(
            (
                "effective_to IS NULL "
                "OR effective_to > effective_from"
            ),
            name=(
                "ck_tax_policies_effective_period"
            )
        ),
    )

    tax_policy_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    rate: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    effective_to: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    created_by: Mapped[
        int | None
    ] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )