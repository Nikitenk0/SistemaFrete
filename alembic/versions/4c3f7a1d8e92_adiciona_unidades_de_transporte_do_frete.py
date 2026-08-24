"""adiciona unidades de transporte do frete

Revision ID: 4c3f7a1d8e92
Revises: 9d7c2e41ab56
Create Date: 2026-08-24 17:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4c3f7a1d8e92"
down_revision: Union[str, Sequence[str], None] = (
    "9d7c2e41ab56"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "freight_transport_units",
        sa.Column(
            "freight_transport_unit_id",
            sa.BigInteger(),
            sa.Identity(always=False),
            nullable=False
        ),
        sa.Column(
            "freight_id",
            sa.BigInteger(),
            nullable=False
        ),
        sa.Column(
            "position",
            sa.SmallInteger(),
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
            "position >= 1",
            name=(
                "ck_freight_transport_units_"
                "position_positive"
            )
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.user_id"],
            name=op.f(
                "fk_freight_transport_units_"
                "created_by_users"
            ),
            ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["freight_id"],
            ["freights.freight_id"],
            name=op.f(
                "fk_freight_transport_units_"
                "freight_id_freights"
            ),
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint(
            "freight_transport_unit_id",
            name=op.f(
                "pk_freight_transport_units"
            )
        ),
        sa.UniqueConstraint(
            "freight_id",
            "position",
            name=(
                "uq_freight_transport_units_"
                "freight_id_position"
            )
        )
    )

    op.create_index(
        op.f(
            "ix_freight_transport_units_freight_id"
        ),
        "freight_transport_units",
        ["freight_id"],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f(
            "ix_freight_transport_units_freight_id"
        ),
        table_name="freight_transport_units"
    )

    op.drop_table(
        "freight_transport_units"
    )
