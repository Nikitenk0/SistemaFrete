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
    func,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from infrastructure.persistence.sqlalchemy.base import Base


class TransportProviderModel(Base):
    __tablename__ = "transport_providers"

    __table_args__ = (
        UniqueConstraint(
            "tax_document",
            name="uq_transport_providers_tax_document",
        ),
        CheckConstraint(
            "provider_type IN ('INDIVIDUAL', 'COMPANY')",
            name="ck_transport_providers_provider_type",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_transport_providers_status",
        ),
        CheckConstraint(
            (
                "(provider_type = 'INDIVIDUAL' "
                "AND char_length(tax_document) = 11) OR "
                "(provider_type = 'COMPANY' "
                "AND char_length(tax_document) = 14)"
            ),
            name="ck_transport_providers_document_length",
        ),
        Index(
            "ix_transport_providers_status",
            "status",
        ),
        Index(
            "ix_transport_providers_legal_name",
            "legal_name",
        ),
    )

    transport_provider_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    legal_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    trade_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    tax_document: Mapped[str] = mapped_column(
        String(14),
        nullable=False,
    )

    provider_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="ACTIVE",
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

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )


class DriverTransportProviderAffiliationModel(Base):
    __tablename__ = "driver_transport_provider_affiliations"

    __table_args__ = (
        CheckConstraint(
            "role IN ('OWNER', 'EMPLOYEE', 'CONTRACTOR')",
            name="ck_driver_transport_provider_role",
        ),
        CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at",
            name="ck_driver_transport_provider_dates",
        ),
        Index(
            "uq_driver_transport_provider_active",
            "driver_id",
            unique=True,
            postgresql_where=text(
                "ended_at IS NULL"
            ),
        ),
        Index(
            "ix_driver_transport_provider_provider",
            "transport_provider_id",
        ),
    )

    driver_transport_provider_affiliation_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    driver_id: Mapped[int] = mapped_column(
        ForeignKey(
            "drivers.driver_id",
            ondelete="RESTRICT",
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

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )


class VehicleTransportProviderAffiliationModel(Base):
    __tablename__ = "vehicle_transport_provider_affiliations"

    __table_args__ = (
        CheckConstraint(
            "relation IN ('OWNED', 'LEASED', 'CONTRACTED')",
            name="ck_vehicle_transport_provider_relation",
        ),
        CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at",
            name="ck_vehicle_transport_provider_dates",
        ),
        Index(
            "uq_vehicle_transport_provider_active",
            "vehicle_id",
            unique=True,
            postgresql_where=text(
                "ended_at IS NULL"
            ),
        ),
        Index(
            "ix_vehicle_transport_provider_provider",
            "transport_provider_id",
        ),
    )

    vehicle_transport_provider_affiliation_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey(
            "vehicles.vehicle_id",
            ondelete="RESTRICT",
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

    relation: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
