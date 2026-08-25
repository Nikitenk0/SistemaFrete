"""adiciona indice para consulta por conclusao do frete

Revision ID: e8f3a1b6c2d9
Revises: c7a1e5d9f2b4
Create Date: 2026-08-25 15:45:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "e8f3a1b6c2d9"
down_revision: Union[str, Sequence[str], None] = "c7a1e5d9f2b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_freights_completed_at",
        "freights",
        ["completed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_freights_completed_at",
        table_name="freights",
    )
