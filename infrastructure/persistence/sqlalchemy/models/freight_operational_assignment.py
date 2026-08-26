from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from infrastructure.persistence.sqlalchemy.base import Base


class FreightOperationalAssignmentModel(Base):
    __tablename__ = "freight_operational_assignments"

    __table_args__ = (
        UniqueConstraint(
            "freight_driver_assignment_id",
            name=(
                "uq_freight_operational_assignments_"
                "driver_assignment"
            ),
        ),
        Index(
            "ix_freight_operational_assignments_provider",
            "transport_provider_id",
        ),
        Index(
            "ix_freight_operational_assignments_vehicle",
            "vehicle_id",
        ),
    )

    freight_operational_assignment_id: Mapped[int] = (
        mapped_column(
            BigInteger,
            Identity(),
            primary_key=True,
        )
    )

    freight_driver_assignment_id: Mapped[int] = mapped_column(
        ForeignKey(
            "freight_driver_assignments.freight_driver_assignment_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    transport_provider_id: Mapped[int] = mapped_column(
        ForeignKey(
            "transport_providers.transport_provider_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey(
            "vehicles.vehicle_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    provider_name_snapshot: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    provider_tax_document_snapshot: Mapped[str] = mapped_column(
        String(14),
        nullable=False,
    )

    driver_name_snapshot: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    driver_cpf_snapshot: Mapped[str] = mapped_column(
        String(11),
        nullable=False,
    )

    vehicle_plate_snapshot: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
    )

    vehicle_type_snapshot: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
