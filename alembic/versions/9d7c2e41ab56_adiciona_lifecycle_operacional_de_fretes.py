"""adiciona lifecycle operacional de fretes

Revision ID: 9d7c2e41ab56
Revises: 06cf4f4e222b
Create Date: 2026-08-24 17:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d7c2e41ab56"
down_revision: Union[str, Sequence[str], None] = (
    "06cf4f4e222b"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "freights",
        sa.Column(
            "current_status",
            sa.String(length=30),
            server_default=sa.text("'PENDING'"),
            nullable=False
        )
    )
    op.add_column(
        "freights",
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )
    op.add_column(
        "freights",
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )
    op.add_column(
        "freights",
        sa.Column(
            "cancelled_at",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    op.create_check_constraint(
        "ck_freights_current_status",
        "freights",
        (
            "current_status IN ("
            "'PENDING', 'IN_PROGRESS', "
            "'COMPLETED', 'CANCELLED'"
            ")"
        )
    )

    op.create_index(
        op.f("ix_freights_current_status"),
        "freights",
        ["current_status"],
        unique=False
    )

    op.create_table(
        "freight_events",
        sa.Column(
            "freight_event_id",
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
            "event_type",
            sa.String(length=40),
            nullable=False
        ),
        sa.Column(
            "previous_status",
            sa.String(length=30),
            nullable=True
        ),
        sa.Column(
            "new_status",
            sa.String(length=30),
            nullable=False
        ),
        sa.Column(
            "observation",
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            nullable=True
        ),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.CheckConstraint(
            (
                "event_type IN ("
                "'CREATED', 'STARTED', "
                "'COMPLETED', 'CANCELLED'"
                ")"
            ),
            name="ck_freight_events_event_type"
        ),
        sa.ForeignKeyConstraint(
            ["freight_id"],
            ["freights.freight_id"],
            name=op.f(
                "fk_freight_events_freight_id_freights"
            ),
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            name=op.f(
                "fk_freight_events_user_id_users"
            ),
            ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint(
            "freight_event_id",
            name=op.f("pk_freight_events")
        )
    )

    op.create_index(
        op.f("ix_freight_events_freight_id"),
        "freight_events",
        ["freight_id"],
        unique=False
    )
    op.create_index(
        op.f("ix_freight_events_occurred_at"),
        "freight_events",
        ["occurred_at"],
        unique=False
    )

    # Os dados atuais são de desenvolvimento, mas manter este
    # backfill deixa qualquer frete já existente consistente com
    # o novo histórico operacional sem exigir reset do banco.
    op.execute(
        sa.text(
            """
            INSERT INTO freight_events (
                freight_id,
                event_type,
                previous_status,
                new_status,
                observation,
                user_id,
                occurred_at
            )
            SELECT
                freight_id,
                'CREATED',
                NULL,
                'PENDING',
                NULL,
                created_by,
                created_at
            FROM freights
            """
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_freight_events_occurred_at"),
        table_name="freight_events"
    )
    op.drop_index(
        op.f("ix_freight_events_freight_id"),
        table_name="freight_events"
    )
    op.drop_table(
        "freight_events"
    )

    op.drop_index(
        op.f("ix_freights_current_status"),
        table_name="freights"
    )
    op.drop_constraint(
        "ck_freights_current_status",
        "freights",
        type_="check"
    )

    op.drop_column(
        "freights",
        "cancelled_at"
    )
    op.drop_column(
        "freights",
        "completed_at"
    )
    op.drop_column(
        "freights",
        "started_at"
    )
    op.drop_column(
        "freights",
        "current_status"
    )
