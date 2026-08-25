from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Numeric,
    UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from infrastructure.persistence.sqlalchemy.base import Base


class FreightFinancialResultModel(Base):

    __tablename__ = "freight_financial_results"

    __table_args__ = (
        UniqueConstraint(
            "freight_id",
            name=(
                "uq_freight_financial_results_freight_id"
            )
        ),
        CheckConstraint(
            "contracted_revenue >= 0",
            name=(
                "ck_freight_financial_results_"
                "contracted_revenue_non_negative"
            )
        ),
        CheckConstraint(
            "actual_driver_amount >= 0",
            name=(
                "ck_freight_financial_results_"
                "actual_driver_amount_non_negative"
            )
        ),
        CheckConstraint(
            "toll_amount >= 0",
            name=(
                "ck_freight_financial_results_"
                "toll_amount_non_negative"
            )
        ),
        CheckConstraint(
            "actual_expenses_total >= 0",
            name=(
                "ck_freight_financial_results_"
                "actual_expenses_total_non_negative"
            )
        ),
        CheckConstraint(
            "freight_insurance_total >= 0",
            name=(
                "ck_ffr_freight_insurance_non_negative"
            )
        ),
        CheckConstraint(
            "tax_total >= 0",
            name=(
                "ck_freight_financial_results_"
                "tax_total_non_negative"
            )
        ),
        CheckConstraint(
            "administrative_cost_allocated >= 0",
            name=(
                "ck_ffr_administrative_cost_non_negative"
            )
        ),
        CheckConstraint(
            "total_cost >= 0",
            name=(
                "ck_freight_financial_results_"
                "total_cost_non_negative"
            )
        ),
        CheckConstraint(
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
        CheckConstraint(
            "realized_result = contracted_revenue - total_cost",
            name=(
                "ck_freight_financial_results_"
                "realized_result_consistent"
            )
        ),
        CheckConstraint(
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
    )

    freight_financial_result_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    freight_id: Mapped[int] = mapped_column(
        ForeignKey(
            "freights.freight_id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    contracted_revenue: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    actual_driver_amount: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    toll_amount: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    actual_expenses_total: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    freight_insurance_total: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    tax_total: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    administrative_cost_allocated: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    total_cost: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    realized_result: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False
    )

    realized_margin: Mapped[Decimal | None] = mapped_column(
        Numeric(),
        nullable=True
    )

    finalized_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    freight = relationship(
        "FreightModel"
    )
