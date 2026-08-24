from types import TracebackType

from sqlalchemy.exc import (
    SQLAlchemyError
)
from sqlalchemy.orm import (
    Session,
    sessionmaker
)

from application.exceptions import (
    QuotePersistenceError
)
from application.ports.quote_number_generator import (
    QuoteNumberGenerator
)
from application.ports.quote_repository import (
    QuoteRepository
)
from application.ports.quote_unit_of_work import (
    QuoteUnitOfWork
)
from infrastructure.persistence.sqlalchemy.quote_number_generator import (
    PostgreSQLQuoteNumberGenerator
)
from infrastructure.persistence.sqlalchemy.quote_repository import (
    SqlAlchemyQuoteRepository
)


class SqlAlchemyQuoteUnitOfWork(
    QuoteUnitOfWork
):

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = (
            session_factory
        )

        self._session: Session | None = None

        self._quotes: (
            QuoteRepository | None
        ) = None

        self._quote_numbers: (
            QuoteNumberGenerator | None
        ) = None

    @property
    def quotes(
        self
    ) -> QuoteRepository:

        if self._quotes is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )

        return self._quotes

    @property
    def quote_numbers(
        self
    ) -> QuoteNumberGenerator:

        if self._quote_numbers is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )

        return self._quote_numbers

    def __enter__(
        self
    ) -> "SqlAlchemyQuoteUnitOfWork":

        self._session = (
            self._session_factory()
        )

        self._quotes = (
            SqlAlchemyQuoteRepository(
                self._session
            )
        )

        self._quote_numbers = (
            PostgreSQLQuoteNumberGenerator(
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
            self._quotes = None
            self._quote_numbers = None

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

            raise QuotePersistenceError(
                "Não foi possível confirmar "
                "a operação com o orçamento"
            ) from error

    def rollback(
        self
    ) -> None:

        if self._session is not None:
            self._session.rollback()


class SqlAlchemyQuoteUnitOfWorkFactory:

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = (
            session_factory
        )

    def create(
        self
    ) -> SqlAlchemyQuoteUnitOfWork:

        return SqlAlchemyQuoteUnitOfWork(
            self._session_factory
        )