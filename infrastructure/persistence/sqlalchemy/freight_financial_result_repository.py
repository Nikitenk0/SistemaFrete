from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from application.exceptions import (
    FreightFinancialResultPersistenceError
)
from application.ports.freight_financial_result_repository import (
    FreightFinancialResultRepository
)
from domain.models.freight_financial_result import (
    FreightFinancialResult
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightFinancialResultModel
)


class SqlAlchemyFreightFinancialResultRepository(
    FreightFinancialResultRepository
):

    def __init__(self, session: Session):
        self._session = session

    def add(
        self,
        financial_result: FreightFinancialResult
    ) -> FreightFinancialResult:

        if (
            financial_result.freight_financial_result_id
            is not None
        ):
            raise ValueError(
                "Fechamento financeiro já possui id"
            )

        model = self._to_model(
            financial_result
        )
        self._session.add(model)

        try:
            self._session.flush()
        except SQLAlchemyError as error:
            raise FreightFinancialResultPersistenceError(
                "Não foi possível salvar o fechamento financeiro do frete"
            ) from error

        return self._to_domain(model)

    def get_by_freight_id(
        self,
        freight_id: int
    ) -> FreightFinancialResult | None:

        try:
            model = self._session.scalar(
                select(
                    FreightFinancialResultModel
                ).where(
                    FreightFinancialResultModel.freight_id
                    == freight_id
                )
            )
        except SQLAlchemyError as error:
            raise FreightFinancialResultPersistenceError(
                "Não foi possível consultar o fechamento financeiro do frete"
            ) from error

        if model is None:
            return None

        return self._to_domain(model)

    @staticmethod
    def _to_model(
        financial_result: FreightFinancialResult
    ) -> FreightFinancialResultModel:

        return FreightFinancialResultModel(
            freight_id=financial_result.freight_id,
            contracted_revenue=(
                financial_result.contracted_revenue
            ),
            actual_driver_amount=(
                financial_result.actual_driver_amount
            ),
            toll_amount=financial_result.toll_amount,
            actual_expenses_total=(
                financial_result.actual_expenses_total
            ),
            freight_insurance_total=(
                financial_result.freight_insurance_total
            ),
            tax_total=financial_result.tax_total,
            administrative_cost_allocated=(
                financial_result.administrative_cost_allocated
            ),
            total_cost=financial_result.total_cost,
            realized_result=financial_result.realized_result,
            realized_margin=financial_result.realized_margin,
            finalized_at=financial_result.finalized_at
        )

    @staticmethod
    def _to_domain(
        model: FreightFinancialResultModel
    ) -> FreightFinancialResult:

        return FreightFinancialResult(
            freight_financial_result_id=(
                model.freight_financial_result_id
            ),
            freight_id=model.freight_id,
            contracted_revenue=model.contracted_revenue,
            actual_driver_amount=model.actual_driver_amount,
            toll_amount=model.toll_amount,
            actual_expenses_total=(
                model.actual_expenses_total
            ),
            freight_insurance_total=(
                model.freight_insurance_total
            ),
            tax_total=model.tax_total,
            administrative_cost_allocated=(
                model.administrative_cost_allocated
            ),
            total_cost=model.total_cost,
            realized_result=model.realized_result,
            realized_margin=model.realized_margin,
            finalized_at=model.finalized_at
        )
