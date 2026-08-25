from types import TracebackType

from sqlalchemy.exc import (
    SQLAlchemyError
)
from sqlalchemy.orm import (
    Session,
    sessionmaker
)

from application.exceptions import (
    DriverPersistenceError
)
from application.ports.driver_repository import (
    DriverRepository
)
from application.ports.driver_unit_of_work import (
    DriverUnitOfWork
)
from infrastructure.persistence.sqlalchemy.driver_repository import (
    SqlAlchemyDriverRepository
)


class SqlAlchemyDriverUnitOfWork(
    DriverUnitOfWork
):

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = session_factory
        self._session: Session | None = None
        self._drivers: DriverRepository | None = None

    @property
    def drivers(
        self
    ) -> DriverRepository:

        if self._drivers is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )

        return self._drivers

    def __enter__(
        self
    ) -> "SqlAlchemyDriverUnitOfWork":

        self._session = self._session_factory()
        self._drivers = SqlAlchemyDriverRepository(
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
            self._drivers = None

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

            raise DriverPersistenceError(
                "Não foi possível confirmar "
                "a operação com o motorista"
            ) from error

    def rollback(
        self
    ) -> None:

        if self._session is not None:
            self._session.rollback()


class SqlAlchemyDriverUnitOfWorkFactory:

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = session_factory

    def create(
        self
    ) -> SqlAlchemyDriverUnitOfWork:

        return SqlAlchemyDriverUnitOfWork(
            self._session_factory
        )
