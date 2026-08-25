from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Numeric,
    String,
    Text,
    func,
    text
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from infrastructure.persistence.sqlalchemy.base import Base


class FreightExpenseModel(Base):

    __tablename__ = "freight_expenses"

    __table_args__ = (
        CheckConstraint(
            (
                "expense_type IN ("
                "'AJUDANTE', 'DESCARGA', 'EMPILHADEIRA', "
                "'MUNCK', 'PALETEIRA', 'OUTROS'"
                ")"
            ),
            name="ck_freight_expenses_expense_type"
        ),
        CheckConstraint(
            "value > 0",
            name="ck_freight_expenses_value_positive"
        ),
        CheckConstraint(
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
    )

    freight_expense_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True
    )

    freight_id: Mapped[int] = mapped_column(
        ForeignKey(
            "freights.freight_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    expense_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    custom_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    value: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    observation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_considered: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    freight = relationship(
        "FreightModel"
    )
