"""adiciona cadastro mestre de veiculos

Revision ID: f4c1a2d7e9b3
Revises: e8f3a1b6c2d9
Create Date: 2026-08-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f4c1a2d7e9b3"
down_revision: Union[str, None] = "e8f3a1b6c2d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column(
            "vehicle_id",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False
        ),
        sa.Column(
            "plate",
            sa.String(length=7),
            nullable=False
        ),
        sa.Column(
            "vehicle_type",
            sa.String(length=30),
            nullable=False
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="ACTIVE",
            nullable=False
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
                "status IN ('ACTIVE', 'INACTIVE')"
            ),
            name="ck_vehicles_status"
        ),
        sa.CheckConstraint(
            (
                "vehicle_type IN ("
                "'CAMINHAO_3_4', 'TOCO', 'TRUCK', "
                "'BITRUCK', 'CARRETA', 'CARRETA_LS', "
                "'CARRETA_VANDERLEIA'"
                ")"
            ),
            name="ck_vehicles_vehicle_type"
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.user_id"],
            ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.user_id"],
            ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint(
            "vehicle_id"
        ),
        sa.UniqueConstraint(
            "plate",
            name="uq_vehicles_plate"
        )
    )

    op.create_index(
        "ix_vehicles_status",
        "vehicles",
        ["status"],
        unique=False
    )
    op.create_index(
        "ix_vehicles_vehicle_type",
        "vehicles",
        ["vehicle_type"],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_vehicles_vehicle_type",
        table_name="vehicles"
    )
    op.drop_index(
        "ix_vehicles_status",
        table_name="vehicles"
    )
    op.drop_table(
        "vehicles"
    )
