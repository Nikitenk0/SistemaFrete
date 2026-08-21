from types import TracebackType

from sqlalchemy.exc import (
    SQLAlchemyError
)
from sqlalchemy.orm import (
    Session,
    sessionmaker
)

from application.exceptions import (
    CustomerPersistenceError
)
from application.ports.customer_repository import (
    CustomerRepository
)
from application.ports.customer_unit_of_work import (
    CustomerUnitOfWork
)
from infrastructure.persistence.sqlalchemy.customer_repository import (
    SqlAlchemyCustomerRepository
)


class SqlAlchemyCustomerUnitOfWork(
    CustomerUnitOfWork
):

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = (
            session_factory
        )

        self._session: Session | None = None

        self._customers: (
            CustomerRepository | None
        ) = None

    @property
    def customers(
        self
    ) -> CustomerRepository:

        if self._customers is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )

        return self._customers

    def __enter__(
        self
    ) -> "SqlAlchemyCustomerUnitOfWork":

        self._session = (
            self._session_factory()
        )

        self._customers = (
            SqlAlchemyCustomerRepository(
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
            self._customers = None

    def commit(
        self
    ) -> None:

        if self._session is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )

        try:

            self._session.commit()

        except SQLAlchemyError as error:

            self._session.rollback()

            raise CustomerPersistenceError(
                "Não foi possível confirmar "
                "a operação com o cliente"
            ) from error

    def rollback(
        self
    ) -> None:

        if self._session is not None:
            self._session.rollback()


class SqlAlchemyCustomerUnitOfWorkFactory:

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = (
            session_factory
        )

    def create(
        self
    ) -> SqlAlchemyCustomerUnitOfWork:

        return SqlAlchemyCustomerUnitOfWork(
            self._session_factory
        )