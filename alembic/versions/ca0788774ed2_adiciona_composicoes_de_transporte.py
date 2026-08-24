"""adiciona composicoes de transporte

Revision ID: ca0788774ed2
Revises: af092e25ba90
Create Date: 2026-08-24 11:13:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ca0788774ed2"
down_revision: Union[
    str,
    Sequence[str],
    None
] = "af092e25ba90"
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


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "quote_transport_compositions",
        sa.Column(
            "quote_transport_composition_id",
            sa.BigInteger(),
            sa.Identity(always=False),
            nullable=False
        ),
        sa.Column(
            "quote_version_id",
            sa.BigInteger(),
            nullable=False
        ),
        sa.Column(
            "position",
            sa.SmallInteger(),
            nullable=False
        ),
        sa.Column(
            "axle_count",
            sa.SmallInteger(),
            nullable=False
        ),
        sa.Column(
            "include_return_trip",
            sa.Boolean(),
            nullable=False
        ),
        sa.Column(
            "distance_km",
            sa.Numeric(),
            nullable=True
        ),
        sa.Column(
            "driver_amount",
            sa.Numeric(),
            nullable=True
        ),
        sa.Column(
            "toll_amount",
            sa.Numeric(),
            nullable=True
        ),
        sa.CheckConstraint(
            "position >= 1",
            name=(
                "ck_quote_transport_compositions_"
                "position_positive"
            )
        ),
        sa.CheckConstraint(
            "axle_count >= 1",
            name=(
                "ck_quote_transport_compositions_"
                "axle_count_positive"
            )
        ),
        sa.CheckConstraint(
            (
                "distance_km IS NULL "
                "OR distance_km >= 0"
            ),
            name=(
                "ck_quote_transport_compositions_"
                "distance_non_negative"
            )
        ),
        sa.CheckConstraint(
            (
                "driver_amount IS NULL "
                "OR driver_amount >= 0"
            ),
            name=(
                "ck_quote_transport_compositions_"
                "driver_amount_non_negative"
            )
        ),
        sa.CheckConstraint(
            (
                "toll_amount IS NULL "
                "OR toll_amount >= 0"
            ),
            name=(
                "ck_quote_transport_compositions_"
                "toll_amount_non_negative"
            )
        ),
        sa.ForeignKeyConstraint(
            [
                "quote_version_id"
            ],
            [
                "quote_versions.quote_version_id"
            ],
            name=op.f(
                "fk_quote_transport_compositions_"
                "quote_version_id_quote_versions"
            ),
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint(
            "quote_transport_composition_id",
            name=op.f(
                "pk_quote_transport_compositions"
            )
        ),
        sa.UniqueConstraint(
            "quote_version_id",
            "position",
            name=(
                "uq_quote_transport_compositions_"
                "quote_version_id_position"
            )
        )
    )

    op.create_index(
        op.f(
            "ix_quote_transport_compositions_"
            "quote_version_id"
        ),
        "quote_transport_compositions",
        [
            "quote_version_id"
        ],
        unique=False
    )

    # Preserva a estrutura legada de uma única composição
    # quando a versão já possui quantidade de eixos.
    op.execute(
        sa.text(
            """
            INSERT INTO quote_transport_compositions (
                quote_version_id,
                position,
                axle_count,
                include_return_trip,
                distance_km,
                driver_amount,
                toll_amount
            )
            SELECT
                quote_version_id,
                1,
                axle_count,
                include_return_trip,
                distance_km,
                driver_amount,
                toll_amount
            FROM quote_versions
            WHERE axle_count IS NOT NULL
            """
        )
    )

    op.drop_column(
        "quote_versions",
        "distance_km"
    )

    op.drop_column(
        "quote_versions",
        "axle_count"
    )

    op.drop_column(
        "quote_versions",
        "include_return_trip"
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column(
        "quote_versions",
        sa.Column(
            "distance_km",
            sa.Numeric(),
            nullable=True
        )
    )

    op.add_column(
        "quote_versions",
        sa.Column(
            "axle_count",
            sa.SmallInteger(),
            nullable=True
        )
    )

    op.add_column(
        "quote_versions",
        sa.Column(
            "include_return_trip",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False
        )
    )

    # O schema antigo suporta somente uma composição.
    # No downgrade, preserva-se a primeira posição de cada versão.
    op.execute(
        sa.text(
            """
            UPDATE quote_versions AS version
            SET
                axle_count = composition.axle_count,
                include_return_trip = (
                    composition.include_return_trip
                ),
                distance_km = composition.distance_km
            FROM quote_transport_compositions AS composition
            WHERE
                composition.quote_version_id = (
                    version.quote_version_id
                )
                AND composition.position = (
                    SELECT MIN(first_composition.position)
                    FROM quote_transport_compositions
                        AS first_composition
                    WHERE
                        first_composition.quote_version_id = (
                            version.quote_version_id
                        )
                )
            """
        )
    )

    op.alter_column(
        "quote_versions",
        "include_return_trip",
        server_default=None
    )

    op.drop_index(
        op.f(
            "ix_quote_transport_compositions_"
            "quote_version_id"
        ),
        table_name=(
            "quote_transport_compositions"
        )
    )

    op.drop_table(
        "quote_transport_compositions"
    )
