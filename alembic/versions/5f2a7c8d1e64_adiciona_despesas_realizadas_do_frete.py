"""adiciona despesas realizadas do frete

Revision ID: 5f2a7c8d1e64
Revises: 3d8e1f6a2b47
Create Date: 2026-08-25 17:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5f2a7c8d1e64"
down_revision: Union[str, Sequence[str], None] = (
    "3d8e1f6a2b47"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "freight_expenses",
        sa.Column(
            "freight_expense_id",
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
            "expense_type",
            sa.String(length=30),
            nullable=False
        ),
        sa.Column(
            "custom_description",
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            "value",
            sa.Numeric(precision=14, scale=2),
            nullable=False
        ),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.Column(
            "observation",
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            "is_considered",
            sa.Boolean(),
            server_default=sa.text("true"),
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
                "expense_type IN ("
                "'AJUDANTE', 'DESCARGA', 'EMPILHADEIRA', "
                "'MUNCK', 'PALETEIRA', 'OUTROS'"
                ")"
            ),
            name="ck_freight_expenses_expense_type"
        ),
        sa.CheckConstraint(
            "value > 0",
            name="ck_freight_expenses_value_positive"
        ),
        sa.CheckConstraint(
            (
                "(expense_type = 'OUTROS' "
                "AND custom_description IS NOT NULL "
                "AND btrim(custom_description) <> '') OR "
                "(expense_type <> 'OUTROS' "
                "AND custom_description IS NULL)"
            ),
            name=(
                "ck_freight_expenses_"
                "custom_description_by_type"
            )
        ),
        sa.ForeignKeyConstraint(
            ["freight_id"],
            ["freights.freight_id"],
            name=op.f(
                "fk_freight_expenses_freight_id_freights"
            ),
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.user_id"],
            name=op.f(
                "fk_freight_expenses_created_by_users"
            ),
            ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint(
            "freight_expense_id",
            name=op.f("pk_freight_expenses")
        )
    )

    op.create_index(
        op.f("ix_freight_expenses_freight_id"),
        "freight_expenses",
        ["freight_id"],
        unique=False
    )

    op.create_index(
        op.f("ix_freight_expenses_occurred_at"),
        "freight_expenses",
        ["occurred_at"],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_freight_expenses_occurred_at"),
        table_name="freight_expenses"
    )
    op.drop_index(
        op.f("ix_freight_expenses_freight_id"),
        table_name="freight_expenses"
    )
    op.drop_table("freight_expenses")
