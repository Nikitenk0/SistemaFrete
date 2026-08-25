"""adiciona participacoes de motoristas no frete

Revision ID: 7a2f9c4d1e83
Revises: b1e6d3a94f20
Create Date: 2026-08-25 08:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7a2f9c4d1e83"
down_revision: Union[str, Sequence[str], None] = (
    "b1e6d3a94f20"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "freight_driver_assignments",
        sa.Column(
            "freight_driver_assignment_id",
            sa.BigInteger(),
            sa.Identity(always=False),
            nullable=False
        ),
        sa.Column(
            "freight_transport_unit_id",
            sa.BigInteger(),
            nullable=False
        ),
        sa.Column(
            "driver_id",
            sa.BigInteger(),
            nullable=False
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.Column(
            "ended_at",
            sa.DateTime(timezone=True),
            nullable=True
        ),
        sa.Column(
            "actual_driver_amount",
            sa.Numeric(precision=14, scale=2),
            nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.Column(
            "created_by",
            sa.BigInteger(),
            nullable=True
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.Column(
            "updated_by",
            sa.BigInteger(),
            nullable=True
        ),
        sa.CheckConstraint(
            (
                "actual_driver_amount IS NULL OR "
                "actual_driver_amount >= 0"
            ),
            name=(
                "ck_freight_driver_assignments_"
                "actual_driver_amount_non_negative"
            )
        ),
        sa.CheckConstraint(
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
        sa.CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at",
            name=(
                "ck_freight_driver_assignments_"
                "ended_after_started"
            )
        ),
        sa.ForeignKeyConstraint(
            ["freight_transport_unit_id"],
            [
                "freight_transport_units."
                "freight_transport_unit_id"
            ],
            name=op.f(
                "fk_freight_driver_assignments_"
                "freight_transport_unit_id_"
                "freight_transport_units"
            ),
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["driver_id"],
            ["drivers.driver_id"],
            name=op.f(
                "fk_freight_driver_assignments_"
                "driver_id_drivers"
            ),
            ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.user_id"],
            name=op.f(
                "fk_freight_driver_assignments_"
                "created_by_users"
            ),
            ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.user_id"],
            name=op.f(
                "fk_freight_driver_assignments_"
                "updated_by_users"
            ),
            ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint(
            "freight_driver_assignment_id",
            name=op.f(
                "pk_freight_driver_assignments"
            )
        )
    )

    op.create_index(
        op.f(
            "ix_freight_driver_assignments_"
            "freight_transport_unit_id"
        ),
        "freight_driver_assignments",
        ["freight_transport_unit_id"],
        unique=False
    )
    op.create_index(
        op.f(
            "ix_freight_driver_assignments_driver_id"
        ),
        "freight_driver_assignments",
        ["driver_id"],
        unique=False
    )
    op.create_index(
        op.f(
            "ix_freight_driver_assignments_started_at"
        ),
        "freight_driver_assignments",
        ["started_at"],
        unique=False
    )
    op.create_index(
        "uq_freight_driver_assignments_active_unit",
        "freight_driver_assignments",
        ["freight_transport_unit_id"],
        unique=True,
        postgresql_where=sa.text(
            "ended_at IS NULL"
        )
    )
    op.create_index(
        "uq_freight_driver_assignments_active_driver",
        "freight_driver_assignments",
        ["driver_id"],
        unique=True,
        postgresql_where=sa.text(
            "ended_at IS NULL"
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "uq_freight_driver_assignments_active_driver",
        table_name="freight_driver_assignments"
    )
    op.drop_index(
        "uq_freight_driver_assignments_active_unit",
        table_name="freight_driver_assignments"
    )
    op.drop_index(
        op.f(
            "ix_freight_driver_assignments_started_at"
        ),
        table_name="freight_driver_assignments"
    )
    op.drop_index(
        op.f(
            "ix_freight_driver_assignments_driver_id"
        ),
        table_name="freight_driver_assignments"
    )
    op.drop_index(
        op.f(
            "ix_freight_driver_assignments_"
            "freight_transport_unit_id"
        ),
        table_name="freight_driver_assignments"
    )
    op.drop_table(
        "freight_driver_assignments"
    )
