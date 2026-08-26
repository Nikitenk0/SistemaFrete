"""adiciona prestadores e vinculos operacionais

Revision ID: b8e4d1c7a2f6
Revises: a7d5c9e2f1b4
Create Date: 2026-08-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b8e4d1c7a2f6"
down_revision: Union[str, None] = "a7d5c9e2f1b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "transport_providers",
        sa.Column(
            "transport_provider_id",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("trade_name", sa.String(length=255), nullable=True),
        sa.Column("tax_document", sa.String(length=14), nullable=False),
        sa.Column("provider_type", sa.String(length=20), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="ACTIVE",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.CheckConstraint(
            "provider_type IN ('INDIVIDUAL', 'COMPANY')",
            name="ck_transport_providers_provider_type",
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_transport_providers_status",
        ),
        sa.CheckConstraint(
            (
                "(provider_type = 'INDIVIDUAL' "
                "AND char_length(tax_document) = 11) OR "
                "(provider_type = 'COMPANY' "
                "AND char_length(tax_document) = 14)"
            ),
            name="ck_transport_providers_document_length",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.user_id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.user_id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("transport_provider_id"),
        sa.UniqueConstraint(
            "tax_document",
            name="uq_transport_providers_tax_document",
        ),
    )

    op.create_index(
        "ix_transport_providers_status",
        "transport_providers",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_transport_providers_legal_name",
        "transport_providers",
        ["legal_name"],
        unique=False,
    )

    op.create_table(
        "driver_transport_provider_affiliations",
        sa.Column(
            "driver_transport_provider_affiliation_id",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
        sa.Column("driver_id", sa.BigInteger(), nullable=False),
        sa.Column("transport_provider_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.CheckConstraint(
            "role IN ('OWNER', 'EMPLOYEE', 'CONTRACTOR')",
            name="ck_driver_transport_provider_role",
        ),
        sa.CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at",
            name="ck_driver_transport_provider_dates",
        ),
        sa.ForeignKeyConstraint(
            ["driver_id"],
            ["drivers.driver_id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["transport_provider_id"],
            ["transport_providers.transport_provider_id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.user_id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.user_id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "driver_transport_provider_affiliation_id"
        ),
    )

    op.create_index(
        "uq_driver_transport_provider_active",
        "driver_transport_provider_affiliations",
        ["driver_id"],
        unique=True,
        postgresql_where=sa.text("ended_at IS NULL"),
    )
    op.create_index(
        "ix_driver_transport_provider_provider",
        "driver_transport_provider_affiliations",
        ["transport_provider_id"],
        unique=False,
    )

    op.create_table(
        "vehicle_transport_provider_affiliations",
        sa.Column(
            "vehicle_transport_provider_affiliation_id",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
        sa.Column("vehicle_id", sa.BigInteger(), nullable=False),
        sa.Column("transport_provider_id", sa.BigInteger(), nullable=False),
        sa.Column("relation", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.CheckConstraint(
            "relation IN ('OWNED', 'LEASED', 'CONTRACTED')",
            name="ck_vehicle_transport_provider_relation",
        ),
        sa.CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at",
            name="ck_vehicle_transport_provider_dates",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicles.vehicle_id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["transport_provider_id"],
            ["transport_providers.transport_provider_id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.user_id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.user_id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "vehicle_transport_provider_affiliation_id"
        ),
    )

    op.create_index(
        "uq_vehicle_transport_provider_active",
        "vehicle_transport_provider_affiliations",
        ["vehicle_id"],
        unique=True,
        postgresql_where=sa.text("ended_at IS NULL"),
    )
    op.create_index(
        "ix_vehicle_transport_provider_provider",
        "vehicle_transport_provider_affiliations",
        ["transport_provider_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_vehicle_transport_provider_provider",
        table_name="vehicle_transport_provider_affiliations",
    )
    op.drop_index(
        "uq_vehicle_transport_provider_active",
        table_name="vehicle_transport_provider_affiliations",
    )
    op.drop_table("vehicle_transport_provider_affiliations")

    op.drop_index(
        "ix_driver_transport_provider_provider",
        table_name="driver_transport_provider_affiliations",
    )
    op.drop_index(
        "uq_driver_transport_provider_active",
        table_name="driver_transport_provider_affiliations",
    )
    op.drop_table("driver_transport_provider_affiliations")

    op.drop_index(
        "ix_transport_providers_legal_name",
        table_name="transport_providers",
    )
    op.drop_index(
        "ix_transport_providers_status",
        table_name="transport_providers",
    )
    op.drop_table("transport_providers")
