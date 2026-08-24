"""adiciona politicas de precificacao

Revision ID: af092e25ba90
Revises: 61ba7dfb049c
Create Date: 2026-08-24 09:31:14.770339

"""

from datetime import (
    datetime,
    timezone
)
from decimal import Decimal
from typing import (
    Sequence,
    Union
)

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "af092e25ba90"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "61ba7dfb049c"

branch_labels: Union[
    str,
    Sequence[str],
    None
] = None

depends_on: Union[
    str,
    Sequence[str],
    None
] = None


INITIAL_EFFECTIVE_FROM = datetime(
    2026,
    8,
    24,
    0,
    0,
    tzinfo=timezone.utc
)


def upgrade() -> None:
    """Upgrade schema."""

    # ==========================================================
    # POLÍTICAS DE CUSTO ADMINISTRATIVO
    # ==========================================================

    op.create_table(
        "administrative_cost_policies",
        sa.Column(
            "administrative_cost_policy_id",
            sa.BigInteger(),
            sa.Identity(always=False),
            nullable=False
        ),
        sa.Column(
            "tracking_required",
            sa.Boolean(),
            nullable=False
        ),
        sa.Column(
            "rate",
            sa.Numeric(),
            nullable=False
        ),
        sa.Column(
            "minimum_value",
            sa.Numeric(),
            nullable=False
        ),
        sa.Column(
            "effective_from",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.Column(
            "effective_to",
            sa.DateTime(timezone=True),
            nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text(
                "now()"
            ),
            nullable=False
        ),
        sa.Column(
            "created_by",
            sa.BigInteger(),
            nullable=True
        ),
        sa.CheckConstraint(
            "rate >= 0 AND rate < 1",
            name=(
                "ck_administrative_cost_policies_"
                "rate"
            )
        ),
        sa.CheckConstraint(
            "minimum_value >= 0",
            name=(
                "ck_administrative_cost_policies_"
                "minimum_value"
            )
        ),
        sa.CheckConstraint(
            (
                "effective_to IS NULL "
                "OR effective_to > effective_from"
            ),
            name=(
                "ck_administrative_cost_policies_"
                "effective_period"
            )
        ),
        sa.ForeignKeyConstraint(
            [
                "created_by"
            ],
            [
                "users.user_id"
            ],
            name=op.f(
                "fk_administrative_cost_policies_"
                "created_by_users"
            ),
            ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint(
            "administrative_cost_policy_id",
            name=op.f(
                "pk_administrative_cost_policies"
            )
        )
    )

    op.create_index(
        op.f(
            "ix_administrative_cost_policies_"
            "effective_from"
        ),
        "administrative_cost_policies",
        [
            "effective_from"
        ],
        unique=False
    )

    op.create_index(
        op.f(
            "ix_administrative_cost_policies_"
            "tracking_required"
        ),
        "administrative_cost_policies",
        [
            "tracking_required"
        ],
        unique=False
    )

    # ==========================================================
    # TABELAS DE MARGEM
    # ==========================================================

    op.create_table(
        "margin_tables",
        sa.Column(
            "margin_table_id",
            sa.BigInteger(),
            sa.Identity(always=False),
            nullable=False
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False
        ),
        sa.Column(
            "effective_from",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.Column(
            "effective_to",
            sa.DateTime(timezone=True),
            nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text(
                "now()"
            ),
            nullable=False
        ),
        sa.Column(
            "created_by",
            sa.BigInteger(),
            nullable=True
        ),
        sa.CheckConstraint(
            (
                "effective_to IS NULL "
                "OR effective_to > effective_from"
            ),
            name=(
                "ck_margin_tables_effective_period"
            )
        ),
        sa.ForeignKeyConstraint(
            [
                "created_by"
            ],
            [
                "users.user_id"
            ],
            name=op.f(
                "fk_margin_tables_created_by_users"
            ),
            ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint(
            "margin_table_id",
            name=op.f(
                "pk_margin_tables"
            )
        )
    )

    op.create_index(
        op.f(
            "ix_margin_tables_effective_from"
        ),
        "margin_tables",
        [
            "effective_from"
        ],
        unique=False
    )

    # ==========================================================
    # POLÍTICAS TRIBUTÁRIAS
    # ==========================================================

    op.create_table(
        "tax_policies",
        sa.Column(
            "tax_policy_id",
            sa.BigInteger(),
            sa.Identity(always=False),
            nullable=False
        ),
        sa.Column(
            "rate",
            sa.Numeric(),
            nullable=False
        ),
        sa.Column(
            "effective_from",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.Column(
            "effective_to",
            sa.DateTime(timezone=True),
            nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text(
                "now()"
            ),
            nullable=False
        ),
        sa.Column(
            "created_by",
            sa.BigInteger(),
            nullable=True
        ),
        sa.CheckConstraint(
            "rate >= 0 AND rate < 1",
            name="ck_tax_policies_rate"
        ),
        sa.CheckConstraint(
            (
                "effective_to IS NULL "
                "OR effective_to > effective_from"
            ),
            name=(
                "ck_tax_policies_effective_period"
            )
        ),
        sa.ForeignKeyConstraint(
            [
                "created_by"
            ],
            [
                "users.user_id"
            ],
            name=op.f(
                "fk_tax_policies_created_by_users"
            ),
            ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint(
            "tax_policy_id",
            name=op.f(
                "pk_tax_policies"
            )
        )
    )

    op.create_index(
        op.f(
            "ix_tax_policies_effective_from"
        ),
        "tax_policies",
        [
            "effective_from"
        ],
        unique=False
    )

    # ==========================================================
    # FAIXAS DE MARGEM
    # ==========================================================

    op.create_table(
        "margin_bands",
        sa.Column(
            "margin_band_id",
            sa.BigInteger(),
            sa.Identity(always=False),
            nullable=False
        ),
        sa.Column(
            "margin_table_id",
            sa.BigInteger(),
            nullable=False
        ),
        sa.Column(
            "position",
            sa.SmallInteger(),
            nullable=False
        ),
        sa.Column(
            "lower_bound_exclusive",
            sa.Numeric(),
            nullable=True
        ),
        sa.Column(
            "upper_bound_inclusive",
            sa.Numeric(),
            nullable=True
        ),
        sa.Column(
            "rate",
            sa.Numeric(),
            nullable=False
        ),
        sa.CheckConstraint(
            "position >= 1",
            name=(
                "ck_margin_bands_position"
            )
        ),
        sa.CheckConstraint(
            "rate >= 0 AND rate < 1",
            name=(
                "ck_margin_bands_rate"
            )
        ),
        sa.CheckConstraint(
            (
                "lower_bound_exclusive IS NULL "
                "OR lower_bound_exclusive >= 0"
            ),
            name=(
                "ck_margin_bands_lower_bound"
            )
        ),
        sa.CheckConstraint(
            (
                "upper_bound_inclusive IS NULL "
                "OR upper_bound_inclusive >= 0"
            ),
            name=(
                "ck_margin_bands_upper_bound"
            )
        ),
        sa.CheckConstraint(
            (
                "lower_bound_exclusive IS NULL "
                "OR upper_bound_inclusive IS NULL "
                "OR upper_bound_inclusive "
                "> lower_bound_exclusive"
            ),
            name=(
                "ck_margin_bands_bounds"
            )
        ),
        sa.ForeignKeyConstraint(
            [
                "margin_table_id"
            ],
            [
                "margin_tables.margin_table_id"
            ],
            name=op.f(
                "fk_margin_bands_"
                "margin_table_id_margin_tables"
            ),
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint(
            "margin_band_id",
            name=op.f(
                "pk_margin_bands"
            )
        ),
        sa.UniqueConstraint(
            "margin_table_id",
            "position",
            name=(
                "uq_margin_bands_"
                "margin_table_id_position"
            )
        )
    )

    op.create_index(
        op.f(
            "ix_margin_bands_margin_table_id"
        ),
        "margin_bands",
        [
            "margin_table_id"
        ],
        unique=False
    )

    # ==========================================================
    # SEED INICIAL
    # ==========================================================

    connection = op.get_bind()

    # ----------------------------------------------------------
    # CUSTO ADMINISTRATIVO
    #
    # Sem rastreamento:
    # 4%, mínimo R$ 200
    #
    # Com rastreamento:
    # 7%, mínimo R$ 200
    # ----------------------------------------------------------

    connection.execute(
        sa.text(
            """
            INSERT INTO administrative_cost_policies (
                tracking_required,
                rate,
                minimum_value,
                effective_from,
                effective_to,
                created_by
            )
            VALUES (
                :tracking_required,
                :rate,
                :minimum_value,
                :effective_from,
                NULL,
                NULL
            )
            """
        ),
        [
            {
                "tracking_required": False,
                "rate": Decimal(
                    "0.04"
                ),
                "minimum_value": Decimal(
                    "200"
                ),
                "effective_from": (
                    INITIAL_EFFECTIVE_FROM
                )
            },
            {
                "tracking_required": True,
                "rate": Decimal(
                    "0.07"
                ),
                "minimum_value": Decimal(
                    "200"
                ),
                "effective_from": (
                    INITIAL_EFFECTIVE_FROM
                )
            }
        ]
    )

    # ----------------------------------------------------------
    # TABELA PADRÃO DE MARGENS
    # ----------------------------------------------------------

    margin_table_id = connection.execute(
        sa.text(
            """
            INSERT INTO margin_tables (
                name,
                effective_from,
                effective_to,
                created_by
            )
            VALUES (
                :name,
                :effective_from,
                NULL,
                NULL
            )
            RETURNING margin_table_id
            """
        ),
        {
            "name": "Tabela padrão",
            "effective_from": (
                INITIAL_EFFECTIVE_FROM
            )
        }
    ).scalar_one()

    # ----------------------------------------------------------
    # FAIXAS DA TABELA PADRÃO
    #
    # lower_bound_exclusive
    # upper_bound_inclusive
    # ----------------------------------------------------------

    margin_bands = (
        (
            1,
            None,
            Decimal("1000"),
            Decimal("0.25")
        ),
        (
            2,
            Decimal("1000"),
            Decimal("3000"),
            Decimal("0.22")
        ),
        (
            3,
            Decimal("3000"),
            Decimal("6000"),
            Decimal("0.18")
        ),
        (
            4,
            Decimal("6000"),
            Decimal("10000"),
            Decimal("0.18")
        ),
        (
            5,
            Decimal("10000"),
            Decimal("15000"),
            Decimal("0.18")
        ),
        (
            6,
            Decimal("15000"),
            Decimal("20000"),
            Decimal("0.16")
        ),
        (
            7,
            Decimal("20000"),
            Decimal("25000"),
            Decimal("0.156")
        ),
        (
            8,
            Decimal("25000"),
            Decimal("30000"),
            Decimal("0.15")
        ),
        (
            9,
            Decimal("30000"),
            Decimal("35000"),
            Decimal("0.15")
        ),
        (
            10,
            Decimal("35000"),
            Decimal("40000"),
            Decimal("0.15")
        ),
        (
            11,
            Decimal("40000"),
            Decimal("45000"),
            Decimal("0.15")
        ),
        (
            12,
            Decimal("45000"),
            Decimal("50000"),
            Decimal("0.15")
        ),
        (
            13,
            Decimal("50000"),
            None,
            Decimal("0.15")
        )
    )

    connection.execute(
        sa.text(
            """
            INSERT INTO margin_bands (
                margin_table_id,
                position,
                lower_bound_exclusive,
                upper_bound_inclusive,
                rate
            )
            VALUES (
                :margin_table_id,
                :position,
                :lower_bound_exclusive,
                :upper_bound_inclusive,
                :rate
            )
            """
        ),
        [
            {
                "margin_table_id": (
                    margin_table_id
                ),
                "position": position,
                "lower_bound_exclusive": (
                    lower_bound
                ),
                "upper_bound_inclusive": (
                    upper_bound
                ),
                "rate": rate
            }
            for (
                position,
                lower_bound,
                upper_bound,
                rate
            ) in margin_bands
        ]
    )

    # ----------------------------------------------------------
    # IMPOSTO
    #
    # Gross-up: 20%
    # ----------------------------------------------------------

    connection.execute(
        sa.text(
            """
            INSERT INTO tax_policies (
                rate,
                effective_from,
                effective_to,
                created_by
            )
            VALUES (
                :rate,
                :effective_from,
                NULL,
                NULL
            )
            """
        ),
        {
            "rate": Decimal(
                "0.20"
            ),
            "effective_from": (
                INITIAL_EFFECTIVE_FROM
            )
        }
    )


def downgrade() -> None:
    """Downgrade schema."""

    # ==========================================================
    # FAIXAS DE MARGEM
    # ==========================================================

    op.drop_index(
        op.f(
            "ix_margin_bands_margin_table_id"
        ),
        table_name="margin_bands"
    )

    op.drop_table(
        "margin_bands"
    )

    # ==========================================================
    # POLÍTICAS TRIBUTÁRIAS
    # ==========================================================

    op.drop_index(
        op.f(
            "ix_tax_policies_effective_from"
        ),
        table_name="tax_policies"
    )

    op.drop_table(
        "tax_policies"
    )

    # ==========================================================
    # TABELAS DE MARGEM
    # ==========================================================

    op.drop_index(
        op.f(
            "ix_margin_tables_effective_from"
        ),
        table_name="margin_tables"
    )

    op.drop_table(
        "margin_tables"
    )

    # ==========================================================
    # POLÍTICAS DE CUSTO ADMINISTRATIVO
    # ==========================================================

    op.drop_index(
        op.f(
            "ix_administrative_cost_policies_"
            "tracking_required"
        ),
        table_name=(
            "administrative_cost_policies"
        )
    )

    op.drop_index(
        op.f(
            "ix_administrative_cost_policies_"
            "effective_from"
        ),
        table_name=(
            "administrative_cost_policies"
        )
    )

    op.drop_table(
        "administrative_cost_policies"
    )