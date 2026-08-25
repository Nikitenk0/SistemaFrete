"""adiciona veiculos operacionais do frete

Revision ID: 3d8e1f6a2b47
Revises: 7a2f9c4d1e83
Create Date: 2026-08-25 09:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3d8e1f6a2b47"
down_revision: Union[str, Sequence[str], None] = (
    "7a2f9c4d1e83"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


VEHICLE_SPECIFICATION_CHECK = (
    "(vehicle_type = 'CAMINHAO_3_4' "
    "AND axle_count = 2 "
    "AND pallet_capacity_min = 8 "
    "AND pallet_capacity_max = 8 "
    "AND payload_capacity_kg = 3500) OR "
    "(vehicle_type = 'TOCO' "
    "AND axle_count = 2 "
    "AND pallet_capacity_min = 12 "
    "AND pallet_capacity_max = 12 "
    "AND payload_capacity_kg = 6500) OR "
    "(vehicle_type = 'TRUCK' "
    "AND axle_count = 3 "
    "AND pallet_capacity_min = 16 "
    "AND pallet_capacity_max = 20 "
    "AND payload_capacity_kg = 12500) OR "
    "(vehicle_type = 'BITRUCK' "
    "AND axle_count = 4 "
    "AND pallet_capacity_min = 16 "
    "AND pallet_capacity_max = 18 "
    "AND payload_capacity_kg = 17000) OR "
    "(vehicle_type = 'CARRETA' "
    "AND axle_count = 5 "
    "AND pallet_capacity_min = 28 "
    "AND pallet_capacity_max = 28 "
    "AND payload_capacity_kg = 26000) OR "
    "(vehicle_type = 'CARRETA_LS' "
    "AND axle_count = 6 "
    "AND pallet_capacity_min = 28 "
    "AND pallet_capacity_max = 28 "
    "AND payload_capacity_kg = 30000) OR "
    "(vehicle_type = 'CARRETA_VANDERLEIA' "
    "AND axle_count = 6 "
    "AND pallet_capacity_min = 30 "
    "AND pallet_capacity_max = 30 "
    "AND payload_capacity_kg = 35000)"
)


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "freight_vehicle_records",
        sa.Column(
            "freight_vehicle_record_id",
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
            "vehicle_type",
            sa.String(length=30),
            nullable=False
        ),
        sa.Column(
            "plate",
            sa.String(length=7),
            nullable=False
        ),
        sa.Column(
            "axle_count",
            sa.SmallInteger(),
            nullable=False
        ),
        sa.Column(
            "pallet_capacity_min",
            sa.SmallInteger(),
            nullable=False
        ),
        sa.Column(
            "pallet_capacity_max",
            sa.SmallInteger(),
            nullable=False
        ),
        sa.Column(
            "payload_capacity_kg",
            sa.Integer(),
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
        sa.CheckConstraint(
            (
                "vehicle_type IN ("
                "'CAMINHAO_3_4', 'TOCO', 'TRUCK', "
                "'BITRUCK', 'CARRETA', 'CARRETA_LS', "
                "'CARRETA_VANDERLEIA'"
                ")"
            ),
            name=(
                "ck_freight_vehicle_records_"
                "vehicle_type"
            )
        ),
        sa.CheckConstraint(
            "plate ~ '^[A-Z0-9]{7}$'",
            name="ck_freight_vehicle_records_plate"
        ),
        sa.CheckConstraint(
            VEHICLE_SPECIFICATION_CHECK,
            name=(
                "ck_freight_vehicle_records_"
                "specification"
            )
        ),
        sa.ForeignKeyConstraint(
            ["freight_transport_unit_id"],
            [
                "freight_transport_units."
                "freight_transport_unit_id"
            ],
            name=op.f(
                "fk_freight_vehicle_records_"
                "freight_transport_unit_id_"
                "freight_transport_units"
            ),
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.user_id"],
            name=op.f(
                "fk_freight_vehicle_records_"
                "created_by_users"
            ),
            ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint(
            "freight_vehicle_record_id",
            name=op.f(
                "pk_freight_vehicle_records"
            )
        ),
        sa.UniqueConstraint(
            "freight_transport_unit_id",
            name=(
                "uq_freight_vehicle_records_"
                "freight_transport_unit_id"
            )
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table(
        "freight_vehicle_records"
    )
