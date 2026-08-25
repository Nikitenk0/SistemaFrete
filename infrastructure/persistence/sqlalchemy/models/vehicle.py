from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from infrastructure.persistence.sqlalchemy.base import Base


class VehicleModel(Base):

    __tablename__ = "vehicles"

    __table_args__ = (
        UniqueConstraint(
            "plate",
            name="uq_vehicles_plate"
        ),
        CheckConstraint(
            (
                "vehicle_type IN ("
                "'CAMINHAO_3_4', 'TOCO', 'TRUCK', "
                "'BITRUCK', 'CARRETA', 'CARRETA_LS', "
                "'CARRETA_VANDERLEIA'"
                ")"
            ),
            name="ck_vehicles_vehicle_type"
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_vehicles_status"
        ),
        Index(
            "ix_vehicles_vehicle_type",
            "vehicle_type"
        ),
        Index(
            "ix_vehicles_status",
            "status"
        ),
    )

    vehicle_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    plate: Mapped[str] = mapped_column(
        String(7),
        nullable=False
    )

    vehicle_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="ACTIVE"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
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
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )
