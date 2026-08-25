"""adiciona fechamento financeiro do frete

Revision ID: c7a1e5d9f2b4
Revises: 5f2a7c8d1e64
Create Date: 2026-08-25 14:54:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c7a1e5d9f2b4"
down_revision: Union[str, Sequence[str], None] = "5f2a7c8d1e64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "freight_financial_results",
        sa.Column(
            "freight_financial_result_id",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False
        ),
        sa.Column(
            "freight_id",
            sa.BigInteger(),
            nullable=False
        ),
        sa.Column(
            "contracted_revenue",
            sa.Numeric(),
            nullable=False
        ),
        sa.Column(
            "actual_driver_amount",
            sa.Numeric(),
            nullable=False
        ),
        sa.Column(
            "toll_amount",
            sa.Numeric(),
            nullable=False
        ),
        sa.Column(
            "actual_expenses_total",
            sa.Numeric(),
            nullable=False
        ),
        sa.Column(
            "freight_insurance_total",
            sa.Numeric(),
            nullable=False
        ),
        sa.Column(
            "tax_total",
            sa.Numeric(),
            nullable=False
        ),
        sa.Column(
            "administrative_cost_allocated",
            sa.Numeric(),
            nullable=False
        ),
        sa.Column(
            "total_cost",
            sa.Numeric(),
            nullable=False
        ),
        sa.Column(
            "realized_result",
            sa.Numeric(),
            nullable=False
        ),
        sa.Column(
            "realized_margin",
            sa.Numeric(),
            nullable=True
        ),
        sa.Column(
            "finalized_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.CheckConstraint(
            "contracted_revenue >= 0",
            name=(
                "ck_freight_financial_results_"
                "contracted_revenue_non_negative"
            )
        ),
        sa.CheckConstraint(
            "actual_driver_amount >= 0",
            name=(
                "ck_freight_financial_results_"
                "actual_driver_amount_non_negative"
            )
        ),
        sa.CheckConstraint(
            "toll_amount >= 0",
            name=(
                "ck_freight_financial_results_"
                "toll_amount_non_negative"
            )
        ),
        sa.CheckConstraint(
            "actual_expenses_total >= 0",
            name=(
                "ck_freight_financial_results_"
                "actual_expenses_total_non_negative"
            )
        ),
        sa.CheckConstraint(
            "freight_insurance_total >= 0",
            name=(
                "ck_ffr_freight_insurance_non_negative"
            )
        ),
        sa.CheckConstraint(
            "tax_total >= 0",
            name=(
                "ck_freight_financial_results_"
                "tax_total_non_negative"
            )
        ),
        sa.CheckConstraint(
            "administrative_cost_allocated >= 0",
            name=(
                "ck_ffr_administrative_cost_non_negative"
            )
        ),
        sa.CheckConstraint(
            "total_cost >= 0",
            name=(
                "ck_freight_financial_results_"
                "total_cost_non_negative"
            )
        ),
        sa.CheckConstraint(
            (
                "total_cost = actual_driver_amount "
                "+ toll_amount "
                "+ actual_expenses_total "
                "+ freight_insurance_total "
                "+ tax_total "
                "+ administrative_cost_allocated"
            ),
            name=(
                "ck_freight_financial_results_"
                "total_cost_consistent"
            )
        ),
        sa.CheckConstraint(
            "realized_result = contracted_revenue - total_cost",
            name=(
                "ck_freight_financial_results_"
                "realized_result_consistent"
            )
        ),
        sa.CheckConstraint(
            (
                "(total_cost = 0 AND realized_margin IS NULL) "
                "OR "
                "(total_cost <> 0 AND realized_margin IS NOT NULL)"
            ),
            name=(
                "ck_freight_financial_results_"
                "realized_margin_presence"
            )
        ),
        sa.ForeignKeyConstraint(
            ["freight_id"],
            ["freights.freight_id"],
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint(
            "freight_financial_result_id"
        ),
        sa.UniqueConstraint(
            "freight_id",
            name=(
                "uq_freight_financial_results_freight_id"
            )
        )
    )


def downgrade() -> None:
    op.drop_table(
        "freight_financial_results"
    )
