from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
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


class QuoteModel(Base):

    __tablename__ = "quotes"

    quote_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    quote_number: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    modality: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    axle_count: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    include_return_trip: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    origin: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    destination: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    distance: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    valor_nota: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    geral: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    pedagio: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    custo: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    total: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    taxes: Mapped[list[QuoteTaxModel]] = relationship(
        back_populates="quote",
        cascade="all, delete-orphan",
        order_by="QuoteTaxModel.position"
    )


class QuoteTaxModel(Base):

    __tablename__ = "quote_taxes"

    __table_args__ = (
        UniqueConstraint(
            "quote_id",
            "position",
            name=(
                "uq_quote_taxes_"
                "quote_id_position"
            )
        ),
    )

    quote_tax_id: Mapped[int] = mapped_column(
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

    position: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    rate: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    calculation_base: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    value: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    quote: Mapped[QuoteModel] = relationship(
        back_populates="taxes"
    )