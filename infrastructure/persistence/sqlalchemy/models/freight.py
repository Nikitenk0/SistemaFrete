from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from infrastructure.persistence.sqlalchemy.base import Base


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

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
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

    events: Mapped[list[FreightEventModel]] = relationship(
        back_populates="freight",
        cascade="all, delete-orphan",
        order_by="FreightEventModel.freight_event_id"
    )

    transport_units: Mapped[
        list[FreightTransportUnitModel]
    ] = relationship(
        back_populates="freight",
        cascade="all, delete-orphan",
        order_by="FreightTransportUnitModel.position"
    )


class FreightTransportUnitModel(Base):

    __tablename__ = "freight_transport_units"

    __table_args__ = (
        UniqueConstraint(
            "freight_id",
            "position",
            name=(
                "uq_freight_transport_units_"
                "freight_id_position"
            )
        ),
        CheckConstraint(
            "position >= 1",
            name=(
                "ck_freight_transport_units_"
                "position_positive"
            )
        ),
    )

    freight_transport_unit_id: Mapped[int] = mapped_column(
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

    position: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
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

    freight: Mapped[FreightModel] = relationship(
        back_populates="transport_units"
    )

    driver_assignments: Mapped[
        list[FreightDriverAssignmentModel]
    ] = relationship(
        back_populates="transport_unit",
        cascade="all, delete-orphan",
        order_by=(
            "FreightDriverAssignmentModel.started_at, "
            "FreightDriverAssignmentModel."
            "freight_driver_assignment_id"
        )
    )


class FreightDriverAssignmentModel(Base):

    __tablename__ = "freight_driver_assignments"

    __table_args__ = (
        Index(
            "uq_freight_driver_assignments_active_unit",
            "freight_transport_unit_id",
            unique=True,
            postgresql_where=text(
                "ended_at IS NULL"
            )
        ),
        Index(
            "uq_freight_driver_assignments_active_driver",
            "driver_id",
            unique=True,
            postgresql_where=text(
                "ended_at IS NULL"
            )
        ),
        CheckConstraint(
            (
                "actual_driver_amount IS NULL OR "
                "actual_driver_amount >= 0"
            ),
            name=(
                "ck_freight_driver_assignments_"
                "actual_driver_amount_non_negative"
            )
        ),
        CheckConstraint(
            (
                "(ended_at IS NULL AND "
                "actual_driver_amount IS NULL) OR "
                "(ended_at IS NOT NULL AND "
                "actual_driver_amount IS NOT NULL)"
            ),
            name=(
                "ck_freight_driver_assignments_"
                "completion_pair"
            )
        ),
        CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at",
            name=(
                "ck_freight_driver_assignments_"
                "ended_after_started"
            )
        ),
    )

    freight_driver_assignment_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    freight_transport_unit_id: Mapped[int] = mapped_column(
        ForeignKey(
            "freight_transport_units.freight_transport_unit_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    driver_id: Mapped[int] = mapped_column(
        ForeignKey(
            "drivers.driver_id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    actual_driver_amount: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(14, 2),
        nullable=True
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

    transport_unit: Mapped[FreightTransportUnitModel] = relationship(
        back_populates="driver_assignments"
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

    previous_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    new_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    observation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    freight: Mapped[FreightModel] = relationship(
        back_populates="events"
    )
