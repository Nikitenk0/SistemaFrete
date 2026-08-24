from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Identity,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from infrastructure.persistence.sqlalchemy.base import (
    Base
)


class FreightModel(Base):

    __tablename__ = "freights"

    __table_args__ = (
        UniqueConstraint(
            "primary_quote_id",
            name="uq_freights_primary_quote_id"
        ),
    )

    freight_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "customers.customer_id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    primary_quote_id: Mapped[int] = mapped_column(
        ForeignKey(
            "quotes.quote_id",
            ondelete="RESTRICT"
        ),
        nullable=False
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
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )
