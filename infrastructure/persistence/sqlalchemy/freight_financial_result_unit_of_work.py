from types import TracebackType

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (
    Session,
    sessionmaker
)

from application.exceptions import (
    FreightFinancialResultPersistenceError
)
from application.ports.freight_driver_assignment_repository import (
    FreightDriverAssignmentRepository
)
from application.ports.freight_expense_repository import (
    FreightExpenseRepository
)
from application.ports.freight_financial_quote_repository import (
    FreightFinancialQuoteRepository
)
from application.ports.freight_financial_result_repository import (
    FreightFinancialResultRepository
)
from application.ports.freight_financial_result_unit_of_work import (
    FreightFinancialResultUnitOfWork
)
from application.ports.freight_repository import FreightRepository
from infrastructure.persistence.sqlalchemy.freight_driver_assignment_repository import (
    SqlAlchemyFreightDriverAssignmentRepository
)
from infrastructure.persistence.sqlalchemy.freight_expense_repository import (
    SqlAlchemyFreightExpenseRepository
)
from infrastructure.persistence.sqlalchemy.freight_financial_quote_repository import (
    SqlAlchemyFreightFinancialQuoteRepository
)
from infrastructure.persistence.sqlalchemy.freight_financial_result_repository import (
    SqlAlchemyFreightFinancialResultRepository
)
from infrastructure.persistence.sqlalchemy.freight_repository import (
    SqlAlchemyFreightRepository
)


class SqlAlchemyFreightFinancialResultUnitOfWork(
    FreightFinancialResultUnitOfWork
):

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = session_factory
        self._session: Session | None = None
        self._freights: FreightRepository | None = None
        self._quotes: FreightFinancialQuoteRepository | None = None
        self._driver_assignments: (
            FreightDriverAssignmentRepository | None
        ) = None
        self._expenses: FreightExpenseRepository | None = None
        self._financial_results: (
            FreightFinancialResultRepository | None
        ) = None

    @property
    def freights(self) -> FreightRepository:
        if self._freights is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return self._freights

    @property
    def quotes(self) -> FreightFinancialQuoteRepository:
        if self._quotes is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return self._quotes

    @property
    def driver_assignments(
        self
    ) -> FreightDriverAssignmentRepository:
        if self._driver_assignments is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return self._driver_assignments

    @property
    def expenses(self) -> FreightExpenseRepository:
        if self._expenses is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return self._expenses

    @property
    def financial_results(
        self
    ) -> FreightFinancialResultRepository:
        if self._financial_results is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return self._financial_results

    def __enter__(
        self
    ) -> "SqlAlchemyFreightFinancialResultUnitOfWork":

        self._session = self._session_factory()
        self._freights = SqlAlchemyFreightRepository(
            self._session
        )
        self._quotes = SqlAlchemyFreightFinancialQuoteRepository(
            self._session
        )
        self._driver_assignments = (
            SqlAlchemyFreightDriverAssignmentRepository(
                self._session
            )
        )
        self._expenses = SqlAlchemyFreightExpenseRepository(
            self._session
        )
        self._financial_results = (
            SqlAlchemyFreightFinancialResultRepository(
                self._session
            )
        )
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None
    ) -> None:

        try:
            if exception_type is not None:
                self.rollback()
        finally:
            if self._session is not None:
                self._session.close()

            self._session = None
            self._freights = None
            self._quotes = None
            self._driver_assignments = None
            self._expenses = None
            self._financial_results = None

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )

        try:
            self._session.commit()
        except SQLAlchemyError as error:
            self._session.rollback()
            raise FreightFinancialResultPersistenceError(
                "Não foi possível confirmar o fechamento financeiro do frete"
            ) from error

    def rollback(self) -> None:
        if self._session is not None:
            self._session.rollback()


class SqlAlchemyFreightFinancialResultUnitOfWorkFactory:

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = session_factory

    def create(
        self
    ) -> SqlAlchemyFreightFinancialResultUnitOfWork:
        return SqlAlchemyFreightFinancialResultUnitOfWork(
            self._session_factory
        )
