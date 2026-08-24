from datetime import datetime

from sqlalchemy import (
    or_,
    select
)
from sqlalchemy.exc import (
    SQLAlchemyError
)
from sqlalchemy.orm import (
    Session,
    selectinload,
    sessionmaker
)

from application.exceptions import (
    QuotePricingPolicyError
)
from application.ports.quote_pricing_policy_provider import (
    QuotePricingPolicyProvider
)
from domain.models.quote_pricing_policy import (
    AdministrativeCostPolicy,
    MarginBand,
    QuotePricingPolicy
)
from infrastructure.persistence.sqlalchemy.models import (
    AdministrativeCostPolicyModel,
    MarginTableModel,
    TaxPolicyModel
)


class SqlAlchemyQuotePricingPolicyProvider(
    QuotePricingPolicyProvider
):

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = (
            session_factory
        )

    def get_effective_policy(
        self,
        at: datetime
    ) -> QuotePricingPolicy:

        try:

            with self._session_factory() as session:

                without_tracking = (
                    self._get_administrative_policy(
                        session=session,
                        at=at,
                        tracking_required=False
                    )
                )

                with_tracking = (
                    self._get_administrative_policy(
                        session=session,
                        at=at,
                        tracking_required=True
                    )
                )

                margin_table = (
                    self._get_margin_table(
                        session=session,
                        at=at
                    )
                )

                tax_policy = (
                    self._get_tax_policy(
                        session=session,
                        at=at
                    )
                )

        except QuotePricingPolicyError:
            raise

        except SQLAlchemyError as error:

            raise QuotePricingPolicyError(
                "Não foi possível consultar "
                "a política de precificação"
            ) from error

        return QuotePricingPolicy(
            administrative_cost_policies=(
                AdministrativeCostPolicy(
                    tracking_required=False,
                    rate=without_tracking.rate,
                    minimum_value=(
                        without_tracking
                        .minimum_value
                    )
                ),
                AdministrativeCostPolicy(
                    tracking_required=True,
                    rate=with_tracking.rate,
                    minimum_value=(
                        with_tracking
                        .minimum_value
                    )
                ),
            ),
            margin_bands=tuple(
                MarginBand(
                    lower_bound_exclusive=(
                        band
                        .lower_bound_exclusive
                    ),
                    upper_bound_inclusive=(
                        band
                        .upper_bound_inclusive
                    ),
                    rate=band.rate
                )
                for band in margin_table.bands
            ),
            tax_rate=tax_policy.rate
        )

    @staticmethod
    def _active_condition(
        model,
        at: datetime
    ):

        return (
            model.effective_from <= at,
            or_(
                model.effective_to.is_(None),
                model.effective_to > at
            )
        )

    @classmethod
    def _get_administrative_policy(
        cls,
        session: Session,
        at: datetime,
        tracking_required: bool
    ) -> AdministrativeCostPolicyModel:

        rows = session.scalars(
            select(
                AdministrativeCostPolicyModel
            )
            .where(
                *cls._active_condition(
                    AdministrativeCostPolicyModel,
                    at
                ),
                (
                    AdministrativeCostPolicyModel
                    .tracking_required
                    == tracking_required
                )
            )
            .order_by(
                AdministrativeCostPolicyModel
                .effective_from
                .desc()
            )
            .limit(2)
        ).all()

        if len(rows) != 1:
            raise QuotePricingPolicyError(
                "Política administrativa "
                "vigente ausente ou ambígua"
            )

        return rows[0]

    @classmethod
    def _get_margin_table(
        cls,
        session: Session,
        at: datetime
    ) -> MarginTableModel:

        rows = session.scalars(
            select(
                MarginTableModel
            )
            .options(
                selectinload(
                    MarginTableModel.bands
                )
            )
            .where(
                *cls._active_condition(
                    MarginTableModel,
                    at
                )
            )
            .order_by(
                MarginTableModel
                .effective_from
                .desc()
            )
            .limit(2)
        ).all()

        if len(rows) != 1:
            raise QuotePricingPolicyError(
                "Tabela de margens vigente "
                "ausente ou ambígua"
            )

        if not rows[0].bands:
            raise QuotePricingPolicyError(
                "Tabela de margens vigente "
                "não possui faixas"
            )

        return rows[0]

    @classmethod
    def _get_tax_policy(
        cls,
        session: Session,
        at: datetime
    ) -> TaxPolicyModel:

        rows = session.scalars(
            select(
                TaxPolicyModel
            )
            .where(
                *cls._active_condition(
                    TaxPolicyModel,
                    at
                )
            )
            .order_by(
                TaxPolicyModel
                .effective_from
                .desc()
            )
            .limit(2)
        ).all()

        if len(rows) != 1:
            raise QuotePricingPolicyError(
                "Política tributária vigente "
                "ausente ou ambígua"
            )

        return rows[0]