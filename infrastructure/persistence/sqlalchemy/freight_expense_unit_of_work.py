from types import TracebackType

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (
    Session,
    sessionmaker
)

from application.exceptions import (
    FreightExpensePersistenceError
)
from application.ports.freight_expense_repository import (
    FreightExpenseRepository
)
from application.ports.freight_expense_unit_of_work import (
    FreightExpenseUnitOfWork
)
from application.ports.freight_repository import (
    FreightRepository
)
from infrastructure.persistence.sqlalchemy.freight_expense_repository import (
    SqlAlchemyFreightExpenseRepository
)
from infrastructure.persistence.sqlalchemy.freight_repository import (
    SqlAlchemyFreightRepository
)


class SqlAlchemyFreightExpenseUnitOfWork(
    FreightExpenseUnitOfWork
):

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = session_factory
        self._session: Session | None = None
        self._freights: FreightRepository | None = None
        self._expenses: FreightExpenseRepository | None = None

    @property
    def freights(self) -> FreightRepository:
        if self._freights is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return self._freights

    @property
    def expenses(self) -> FreightExpenseRepository:
        if self._expenses is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return self._expenses

    def __enter__(
        self
    ) -> "SqlAlchemyFreightExpenseUnitOfWork":

        self._session = self._session_factory()
        self._freights = SqlAlchemyFreightRepository(
            self._session
        )
        self._expenses = SqlAlchemyFreightExpenseRepository(
            self._session
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
            self._expenses = None

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )

        try:
            self._session.commit()
        except SQLAlchemyError as error:
            self._session.rollback()
            raise FreightExpensePersistenceError(
                "Não foi possível confirmar a operação "
                "da despesa do frete"
            ) from error

    def rollback(self) -> None:
        if self._session is not None:
            self._session.rollback()


class SqlAlchemyFreightExpenseUnitOfWorkFactory:

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = session_factory

    def create(
        self
    ) -> SqlAlchemyFreightExpenseUnitOfWork:
        return SqlAlchemyFreightExpenseUnitOfWork(
            self._session_factory
        )
