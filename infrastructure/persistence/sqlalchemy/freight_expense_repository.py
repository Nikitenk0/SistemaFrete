from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from application.exceptions import (
    FreightExpenseNotFoundError,
    FreightExpensePersistenceError
)
from application.ports.freight_expense_repository import (
    FreightExpenseRepository
)
from domain.models.freight_expense import (
    FreightExpense,
    FreightExpenseType
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightExpenseModel
)


class SqlAlchemyFreightExpenseRepository(
    FreightExpenseRepository
):

    def __init__(self, session: Session):
        self._session = session

    def add(
        self,
        expense: FreightExpense
    ) -> FreightExpense:

        if expense.freight_expense_id is not None:
            raise ValueError(
                "Despesa do frete já possui id"
            )

        model = self._to_model(expense)
        self._session.add(model)

        try:
            self._session.flush()
        except SQLAlchemyError as error:
            raise FreightExpensePersistenceError(
                "Não foi possível salvar a despesa do frete"
            ) from error

        return self._to_domain(model)

    def save(
        self,
        expense: FreightExpense
    ) -> FreightExpense:

        expense_id = expense.freight_expense_id

        if expense_id is None:
            raise ValueError(
                "Despesa do frete não possui id"
            )

        try:
            model = self._session.scalar(
                select(FreightExpenseModel).where(
                    FreightExpenseModel.freight_expense_id
                    == expense_id
                )
            )

            if model is None:
                raise FreightExpenseNotFoundError(
                    "Despesa do frete não encontrada"
                )

            self._validate_immutable_fields(
                model,
                expense
            )

            model.is_considered = expense.is_considered
            self._session.flush()

        except FreightExpenseNotFoundError:
            raise

        except SQLAlchemyError as error:
            raise FreightExpensePersistenceError(
                "Não foi possível atualizar a despesa do frete"
            ) from error

        return self._to_domain(model)

    def get_by_id(
        self,
        freight_expense_id: int
    ) -> FreightExpense | None:

        try:
            model = self._session.scalar(
                select(FreightExpenseModel).where(
                    FreightExpenseModel.freight_expense_id
                    == freight_expense_id
                )
            )
        except SQLAlchemyError as error:
            raise FreightExpensePersistenceError(
                "Não foi possível consultar a despesa do frete"
            ) from error

        if model is None:
            return None

        return self._to_domain(model)

    def list_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightExpense, ...]:

        try:
            models = self._session.scalars(
                select(FreightExpenseModel)
                .where(
                    FreightExpenseModel.freight_id
                    == freight_id
                )
                .order_by(
                    FreightExpenseModel.occurred_at,
                    FreightExpenseModel.freight_expense_id
                )
            ).all()
        except SQLAlchemyError as error:
            raise FreightExpensePersistenceError(
                "Não foi possível consultar as despesas do frete"
            ) from error

        return tuple(
            self._to_domain(model)
            for model in models
        )

    @staticmethod
    def _to_model(
        expense: FreightExpense
    ) -> FreightExpenseModel:

        model = FreightExpenseModel(
            freight_id=expense.freight_id,
            expense_type=expense.expense_type.value,
            custom_description=expense.custom_description,
            value=expense.value,
            occurred_at=expense.occurred_at,
            observation=expense.observation,
            is_considered=expense.is_considered,
            created_by=expense.created_by
        )

        if expense.created_at is not None:
            model.created_at = expense.created_at

        return model

    @staticmethod
    def _to_domain(
        model: FreightExpenseModel
    ) -> FreightExpense:

        return FreightExpense(
            freight_expense_id=model.freight_expense_id,
            freight_id=model.freight_id,
            expense_type=FreightExpenseType(
                model.expense_type
            ),
            custom_description=model.custom_description,
            value=model.value,
            occurred_at=model.occurred_at,
            observation=model.observation,
            is_considered=model.is_considered,
            created_at=model.created_at,
            created_by=model.created_by
        )

    @staticmethod
    def _validate_immutable_fields(
        model: FreightExpenseModel,
        expense: FreightExpense
    ) -> None:

        if (
            model.freight_id != expense.freight_id
            or model.expense_type != expense.expense_type.value
            or model.custom_description != expense.custom_description
            or model.value != expense.value
            or model.occurred_at != expense.occurred_at
            or model.observation != expense.observation
            or model.created_at != expense.created_at
            or model.created_by != expense.created_by
        ):
            raise ValueError(
                "Campos de origem da despesa do frete são imutáveis"
            )
