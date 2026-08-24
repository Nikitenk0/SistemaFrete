from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
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


class FreightModel(Base):

    __tablename__ = "freights"

    __table_args__ = (
        UniqueConstraint(
            "primary_quote_id",
            name="uq_freights_primary_quote_id"
        ),
        CheckConstraint(
            (
                "current_status IN ("
                "'PENDING', 'IN_PROGRESS', "
                "'COMPLETED', 'CANCELLED'"
                ")"
            ),
            name="ck_freights_current_status"
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

    current_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="PENDING",
        index=True
    )

    started_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True
    )

    completed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True
    )

    cancelled_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
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
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    events: Mapped[
        list[FreightEventModel]
    ] = relationship(
        back_populates="freight",
        cascade="all, delete-orphan",
        order_by="FreightEventModel.freight_event_id"
    )


class FreightEventModel(Base):

    __tablename__ = "freight_events"

    __table_args__ = (
        CheckConstraint(
            (
                "event_type IN ("
                "'CREATED', 'STARTED', "
                "'COMPLETED', 'CANCELLED'"
                ")"
            ),
            name="ck_freight_events_event_type"
        ),
    )

    freight_event_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    freight_id: Mapped[int] = mapped_column(
        ForeignKey(
            "freights.freight_id",
            ondelete="CASCADE"
        ),
        nullable=False,
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

    new_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
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

    freight: Mapped[
        FreightModel
    ] = relationship(
        back_populates="events"
    )
