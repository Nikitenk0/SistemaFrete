from types import TracebackType

from sqlalchemy.exc import (
    SQLAlchemyError
)
from sqlalchemy.orm import (
    Session,
    sessionmaker
)

from application.exceptions import (
    FreightPersistenceError
)
from application.ports.freight_driver_assignment_repository import (
    FreightDriverAssignmentRepository
)
from application.ports.freight_repository import (
    FreightRepository
)
from application.ports.freight_transport_unit_repository import (
    FreightTransportUnitRepository
)
from application.ports.freight_unit_of_work import (
    FreightUnitOfWork
)
from application.ports.freight_vehicle_record_repository import (
    FreightVehicleRecordRepository
)
from application.ports.quote_repository import (
    QuoteRepository
)
from infrastructure.persistence.sqlalchemy.freight_driver_assignment_repository import (
    SqlAlchemyFreightDriverAssignmentRepository
)
from infrastructure.persistence.sqlalchemy.freight_repository import (
    SqlAlchemyFreightRepository
)
from infrastructure.persistence.sqlalchemy.freight_transport_unit_repository import (
    SqlAlchemyFreightTransportUnitRepository
)
from infrastructure.persistence.sqlalchemy.freight_vehicle_record_repository import (
    SqlAlchemyFreightVehicleRecordRepository
)
from infrastructure.persistence.sqlalchemy.quote_repository import (
    SqlAlchemyQuoteRepository
)


class SqlAlchemyFreightUnitOfWork(
    FreightUnitOfWork
):

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = (
            session_factory
        )

        self._session: Session | None = None
        self._freights: FreightRepository | None = None
        self._transport_units: (
            FreightTransportUnitRepository | None
        ) = None
        self._driver_assignments: (
            FreightDriverAssignmentRepository | None
        ) = None
        self._vehicle_records: (
            FreightVehicleRecordRepository | None
        ) = None
        self._quotes: QuoteRepository | None = None

    @property
    def freights(
        self
    ) -> FreightRepository:

        if self._freights is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )

        return self._freights

    @property
    def transport_units(
        self
    ) -> FreightTransportUnitRepository:

        if self._transport_units is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )

        return self._transport_units

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
    def vehicle_records(
        self
    ) -> FreightVehicleRecordRepository:

        if self._vehicle_records is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )

        return self._vehicle_records

    @property
    def quotes(
        self
    ) -> QuoteRepository:

        if self._quotes is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )

        return self._quotes

    def __enter__(
        self
    ) -> "SqlAlchemyFreightUnitOfWork":

        self._session = (
            self._session_factory()
        )

        self._freights = (
            SqlAlchemyFreightRepository(
                self._session
            )
        )

        self._transport_units = (
            SqlAlchemyFreightTransportUnitRepository(
                self._session
            )
        )

        self._driver_assignments = (
            SqlAlchemyFreightDriverAssignmentRepository(
                self._session
            )
        )

        self._vehicle_records = (
            SqlAlchemyFreightVehicleRecordRepository(
                self._session
            )
        )

        self._quotes = (
            SqlAlchemyQuoteRepository(
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
            self._transport_units = None
            self._driver_assignments = None
            self._vehicle_records = None
            self._quotes = None

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

            raise FreightPersistenceError(
                "Não foi possível confirmar "
                "a operação do frete"
            ) from error

    def rollback(
        self
    ) -> None:

        if self._session is not None:
            self._session.rollback()


class SqlAlchemyFreightUnitOfWorkFactory:

    def __init__(
        self,
        session_factory: sessionmaker[Session]
    ):
        self._session_factory = (
            session_factory
        )

    def create(
        self
    ) -> SqlAlchemyFreightUnitOfWork:
        return SqlAlchemyFreightUnitOfWork(
            self._session_factory
        )
