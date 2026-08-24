from __future__ import annotations

from datetime import (
    date,
    datetime
)
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Identity,
    Numeric,
    SmallInteger,
    String,
    Text,
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


class QuoteModel(Base):

    __tablename__ = "quotes"

    __table_args__ = (
        CheckConstraint(
            (
                "("
                "quote_type = 'PRIMARY' "
                "AND primary_quote_id IS NULL"
                ") OR ("
                "quote_type = 'COMPLEMENTARY' "
                "AND primary_quote_id IS NOT NULL"
                ")"
            ),
            name="ck_quotes_type_primary_quote"
        ),
        CheckConstraint(
            (
                "primary_quote_id IS NULL "
                "OR primary_quote_id <> quote_id"
            ),
            name="ck_quotes_not_self_primary"
        ),
        CheckConstraint(
            (
                "("
                "current_status = 'APPROVED' "
                "AND approved_version_id IS NOT NULL"
                ") OR ("
                "current_status <> 'APPROVED' "
                "AND approved_version_id IS NULL"
                ")"
            ),
            name="ck_quotes_approved_version"
        ),
        ForeignKeyConstraint(
            [
                "quote_id",
                "approved_version_id"
            ],
            [
                "quote_versions.quote_id",
                "quote_versions.quote_version_id"
            ],
            name=(
                "fk_quotes_approved_version_"
                "quote_versions"
            ),
            use_alter=True,
            ondelete="RESTRICT"
        ),
    )

    quote_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    quote_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )

    quote_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "customers.customer_id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    primary_quote_id: Mapped[
        int | None
    ] = mapped_column(
        ForeignKey(
            "quotes.quote_id",
            ondelete="RESTRICT"
        ),
        nullable=True,
        index=True
    )

    freight_id: Mapped[
        int | None
    ] = mapped_column(
        BigInteger,
        nullable=True,
        index=True
    )

    current_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True
    )

    approved_version_id: Mapped[
        int | None
    ] = mapped_column(
        BigInteger,
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

    created_by: Mapped[
        int | None
    ] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    versions: Mapped[
        list[QuoteVersionModel]
    ] = relationship(
        back_populates="quote",
        cascade="all, delete-orphan",
        order_by="QuoteVersionModel.version_number",
        foreign_keys="QuoteVersionModel.quote_id"
    )

    events: Mapped[
        list[QuoteEventModel]
    ] = relationship(
        back_populates="quote",
        cascade="all, delete-orphan",
        order_by="QuoteEventModel.quote_event_id"
    )


class QuoteVersionModel(Base):

    __tablename__ = "quote_versions"

    __table_args__ = (
        UniqueConstraint(
            "quote_id",
            "version_number",
            name=(
                "uq_quote_versions_"
                "quote_id_version_number"
            )
        ),
        UniqueConstraint(
            "quote_id",
            "quote_version_id",
            name=(
                "uq_quote_versions_"
                "quote_id_quote_version_id"
            )
        ),
        CheckConstraint(
            "version_number >= 1",
            name=(
                "ck_quote_versions_"
                "version_number_positive"
            )
        ),
    )

    quote_version_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    quote_id: Mapped[int] = mapped_column(
        ForeignKey(
            "quotes.quote_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    version_number: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    customer_person_type_snapshot: Mapped[
        str
    ] = mapped_column(
        String(2),
        nullable=False
    )

    customer_document_snapshot: Mapped[
        str
    ] = mapped_column(
        String(14),
        nullable=False
    )

    customer_legal_name_snapshot: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    customer_trade_name_snapshot: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    modality: Mapped[
        str | None
    ] = mapped_column(
        String(30),
        nullable=True
    )

    origin: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    destination: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    distance_km: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    axle_count: Mapped[
        int | None
    ] = mapped_column(
        SmallInteger,
        nullable=True
    )

    include_return_trip: Mapped[
        bool
    ] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    invoice_value: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    tracking_required: Mapped[
        bool
    ] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    driver_amount: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    toll_amount: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    additional_total: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    freight_insurance_total: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    bp01: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    administrative_rate: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    administrative_minimum: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    administrative_cost: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    bp02: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    margin_band_minimum: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    margin_band_maximum: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    standard_margin_rate: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    standard_margin_value: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    target_net_value: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    tax_rate: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    tax_value: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    calculated_price: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    rounded_price: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    offered_price: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    contracted_price: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    offered_margin_value: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    offered_margin_rate: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    contracted_margin_value: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    contracted_margin_rate: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    validity_days_snapshot: Mapped[
        int | None
    ] = mapped_column(
        SmallInteger,
        nullable=True
    )

    valid_until: Mapped[
        date | None
    ] = mapped_column(
        Date,
        nullable=True
    )

    internal_observation: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True
    )

    proposal_observation: Mapped[
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

    quote: Mapped[
        QuoteModel
    ] = relationship(
        back_populates="versions",
        foreign_keys=[quote_id]
    )

    additionals: Mapped[
        list[QuoteAdditionalModel]
    ] = relationship(
        back_populates="quote_version",
        cascade="all, delete-orphan",
        order_by="QuoteAdditionalModel.position"
    )

    insurance_components: Mapped[
        list[QuoteInsuranceComponentModel]
    ] = relationship(
        back_populates="quote_version",
        cascade="all, delete-orphan",
        order_by=(
            "QuoteInsuranceComponentModel.position"
        )
    )


class QuoteAdditionalModel(Base):

    __tablename__ = "quote_additionals"

    __table_args__ = (
        UniqueConstraint(
            "quote_version_id",
            "position",
            name=(
                "uq_quote_additionals_"
                "quote_version_id_position"
            )
        ),
        CheckConstraint(
            "position >= 1",
            name=(
                "ck_quote_additionals_"
                "position_positive"
            )
        ),
    )

    quote_additional_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    quote_version_id: Mapped[int] = mapped_column(
        ForeignKey(
            "quote_versions.quote_version_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    additional_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    custom_description: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True
    )

    value: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    position: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    quote_version: Mapped[
        QuoteVersionModel
    ] = relationship(
        back_populates="additionals"
    )


class QuoteInsuranceComponentModel(Base):

    __tablename__ = (
        "quote_insurance_components"
    )

    __table_args__ = (
        UniqueConstraint(
            "quote_version_id",
            "position",
            name=(
                "uq_quote_insurance_components_"
                "quote_version_id_position"
            )
        ),
        CheckConstraint(
            "position >= 1",
            name=(
                "ck_quote_insurance_components_"
                "position_positive"
            )
        ),
    )

    quote_insurance_component_id: Mapped[
        int
    ] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    quote_version_id: Mapped[int] = mapped_column(
        ForeignKey(
            "quote_versions.quote_version_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    insurance_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    calculation_base: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    rate: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    value: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    position: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    quote_version: Mapped[
        QuoteVersionModel
    ] = relationship(
        back_populates="insurance_components"
    )


class QuoteEventModel(Base):

    __tablename__ = "quote_events"

    quote_event_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    quote_id: Mapped[int] = mapped_column(
        ForeignKey(
            "quotes.quote_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    quote_version_id: Mapped[
        int | None
    ] = mapped_column(
        ForeignKey(
            "quote_versions.quote_version_id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    event_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False
    )

    previous_status: Mapped[
        str | None
    ] = mapped_column(
        String(30),
        nullable=True
    )

    new_status: Mapped[
        str | None
    ] = mapped_column(
        String(30),
        nullable=True
    )

    previous_amount: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    new_amount: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(),
        nullable=True
    )

    reason_code: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True
    )

    observation: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True
    )

    user_id: Mapped[
        int | None
    ] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    quote: Mapped[
        QuoteModel
    ] = relationship(
        back_populates="events"
    )


class QuoteNumberCounterModel(Base):

    __tablename__ = "quote_number_counters"

    year: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True
    )

    last_value: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )