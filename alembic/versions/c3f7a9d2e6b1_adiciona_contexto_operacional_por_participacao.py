"""adiciona contexto operacional por participacao

Revision ID: c3f7a9d2e6b1
Revises: b8e4d1c7a2f6
Create Date: 2026-08-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3f7a9d2e6b1"
down_revision: Union[str, None] = "b8e4d1c7a2f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "freight_operational_assignments",
        sa.Column(
            "freight_operational_assignment_id",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "freight_driver_assignment_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "transport_provider_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "vehicle_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "provider_name_snapshot",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "provider_tax_document_snapshot",
            sa.String(length=14),
            nullable=False,
        ),
        sa.Column(
            "driver_name_snapshot",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "driver_cpf_snapshot",
            sa.String(length=11),
            nullable=False,
        ),
        sa.Column(
            "vehicle_plate_snapshot",
            sa.String(length=7),
            nullable=False,
        ),
        sa.Column(
            "vehicle_type_snapshot",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            sa.BigInteger(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["freight_driver_assignment_id"],
            ["freight_driver_assignments.freight_driver_assignment_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["transport_provider_id"],
            ["transport_providers.transport_provider_id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicles.vehicle_id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.user_id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "freight_operational_assignment_id"
        ),
        sa.UniqueConstraint(
            "freight_driver_assignment_id",
            name=(
                "uq_freight_operational_assignments_"
                "driver_assignment"
            ),
        ),
    )

    op.create_index(
        "ix_freight_operational_assignments_provider",
        "freight_operational_assignments",
        ["transport_provider_id"],
        unique=False,
    )

    op.create_index(
        "ix_freight_operational_assignments_vehicle",
        "freight_operational_assignments",
        ["vehicle_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_freight_operational_assignments_vehicle",
        table_name="freight_operational_assignments",
    )
    op.drop_index(
        "ix_freight_operational_assignments_provider",
        table_name="freight_operational_assignments",
    )
    op.drop_table(
        "freight_operational_assignments"
    )
