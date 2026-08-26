"""vincula snapshot operacional ao veiculo mestre

Revision ID: a7d5c9e2f1b4
Revises: f4c1a2d7e9b3
Create Date: 2026-08-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7d5c9e2f1b4"
down_revision: Union[str, None] = "f4c1a2d7e9b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "freight_vehicle_records",
        sa.Column("vehicle_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_freight_vehicle_records_vehicle_id_vehicles",
        "freight_vehicle_records",
        "vehicles",
        ["vehicle_id"],
        ["vehicle_id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_freight_vehicle_records_vehicle_id",
        "freight_vehicle_records",
        ["vehicle_id"],
        unique=False,
    )
    op.execute(
        sa.text(
            """
            UPDATE freight_vehicle_records AS freight_vehicle
            SET vehicle_id = vehicle.vehicle_id
            FROM vehicles AS vehicle
            WHERE freight_vehicle.vehicle_id IS NULL
              AND freight_vehicle.plate = vehicle.plate
            """
        )
    )


def downgrade() -> None:
    op.drop_index(
        "ix_freight_vehicle_records_vehicle_id",
        table_name="freight_vehicle_records",
    )
    op.drop_constraint(
        "fk_freight_vehicle_records_vehicle_id_vehicles",
        "freight_vehicle_records",
        type_="foreignkey",
    )
    op.drop_column("freight_vehicle_records", "vehicle_id")
