from types import TracebackType

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (
    Session,
    sessionmaker
)

from application.exceptions import (
    VehiclePersistenceError
)
from application.ports.vehicle_repository import (
    VehicleRepository
)
from application.ports.vehicle_unit_of_work import (
    VehicleUnitOfWork
)
from infrastructure.persistence.sqlalchemy.vehicle_repository import (
    SqlAlchemyVehicleRepository
)


class SqlAlchemyVehicleUnitOfWork(
    VehicleUnitOfWork
):

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = session_factory
        self._session: Session | None = None
        self._vehicles: VehicleRepository | None = None

    @property
    def vehicles(
        self
    ) -> VehicleRepository:
        if self._vehicles is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return self._vehicles

    def __enter__(
        self
    ) -> "SqlAlchemyVehicleUnitOfWork":
        self._session = self._session_factory()
        self._vehicles = SqlAlchemyVehicleRepository(
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
            self._vehicles = None

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
            raise VehiclePersistenceError(
                "Não foi possível confirmar a operação com o veículo"
            ) from error

    def rollback(
        self
    ) -> None:
        if self._session is not None:
            self._session.rollback()


class SqlAlchemyVehicleUnitOfWorkFactory:

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = session_factory

    def create(
        self
    ) -> SqlAlchemyVehicleUnitOfWork:
        return SqlAlchemyVehicleUnitOfWork(
            self._session_factory
        )
