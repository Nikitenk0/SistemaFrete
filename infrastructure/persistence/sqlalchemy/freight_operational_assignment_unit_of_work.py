from types import TracebackType

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from application.exceptions import (
    FreightOperationalAssignmentPersistenceError,
)
from application.ports.freight_operational_assignment_unit_of_work import (
    FreightOperationalAssignmentUnitOfWork,
)
from infrastructure.persistence.sqlalchemy.driver_repository import (
    SqlAlchemyDriverRepository,
)
from infrastructure.persistence.sqlalchemy.freight_driver_assignment_repository import (
    SqlAlchemyFreightDriverAssignmentRepository,
)
from infrastructure.persistence.sqlalchemy.freight_operational_assignment_repository import (
    SqlAlchemyFreightOperationalAssignmentRepository,
)
from infrastructure.persistence.sqlalchemy.freight_repository import (
    SqlAlchemyFreightRepository,
)
from infrastructure.persistence.sqlalchemy.freight_transport_unit_repository import (
    SqlAlchemyFreightTransportUnitRepository,
)
from infrastructure.persistence.sqlalchemy.freight_vehicle_record_repository import (
    SqlAlchemyFreightVehicleRecordRepository,
)
from infrastructure.persistence.sqlalchemy.transport_provider_affiliation_repository import (
    SqlAlchemyDriverTransportProviderAffiliationRepository,
    SqlAlchemyVehicleTransportProviderAffiliationRepository,
)
from infrastructure.persistence.sqlalchemy.transport_provider_repository import (
    SqlAlchemyTransportProviderRepository,
)
from infrastructure.persistence.sqlalchemy.vehicle_repository import (
    SqlAlchemyVehicleRepository,
)


class SqlAlchemyFreightOperationalAssignmentUnitOfWork(
    FreightOperationalAssignmentUnitOfWork
):

    def __init__(
        self,
        session_factory: sessionmaker[Session],
    ):
        self._session_factory = session_factory
        self._session: Session | None = None

    def __enter__(
        self,
    ) -> "SqlAlchemyFreightOperationalAssignmentUnitOfWork":
        self._session = self._session_factory()

        self._freights = SqlAlchemyFreightRepository(
            self._session
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
        self._operational_assignments = (
            SqlAlchemyFreightOperationalAssignmentRepository(
                self._session
            )
        )
        self._providers = SqlAlchemyTransportProviderRepository(
            self._session
        )
        self._driver_affiliations = (
            SqlAlchemyDriverTransportProviderAffiliationRepository(
                self._session
            )
        )
        self._vehicle_affiliations = (
            SqlAlchemyVehicleTransportProviderAffiliationRepository(
                self._session
            )
        )
        self._drivers = SqlAlchemyDriverRepository(
            self._session
        )
        self._vehicles = SqlAlchemyVehicleRepository(
            self._session
        )

        return self

    @property
    def freights(self):
        return self._required("_freights")

    @property
    def transport_units(self):
        return self._required("_transport_units")

    @property
    def driver_assignments(self):
        return self._required("_driver_assignments")

    @property
    def vehicle_records(self):
        return self._required("_vehicle_records")

    @property
    def operational_assignments(self):
        return self._required("_operational_assignments")

    @property
    def providers(self):
        return self._required("_providers")

    @property
    def driver_affiliations(self):
        return self._required("_driver_affiliations")

    @property
    def vehicle_affiliations(self):
        return self._required("_vehicle_affiliations")

    @property
    def drivers(self):
        return self._required("_drivers")

    @property
    def vehicles(self):
        return self._required("_vehicles")

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )

        try:
            self._session.commit()
        except SQLAlchemyError as error:
            self._session.rollback()
            raise FreightOperationalAssignmentPersistenceError(
                "Não foi possível confirmar o contexto operacional"
            ) from error

    def rollback(self) -> None:
        if self._session is not None:
            self._session.rollback()

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            if exception_type is not None:
                self.rollback()
        finally:
            if self._session is not None:
                self._session.close()

            self._session = None
            for name in (
                "_freights",
                "_transport_units",
                "_driver_assignments",
                "_vehicle_records",
                "_operational_assignments",
                "_providers",
                "_driver_affiliations",
                "_vehicle_affiliations",
                "_drivers",
                "_vehicles",
            ):
                setattr(self, name, None)

    def _required(self, name):
        value = getattr(self, name, None)
        if value is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return value


class SqlAlchemyFreightOperationalAssignmentUnitOfWorkFactory:

    def __init__(
        self,
        session_factory: sessionmaker[Session],
    ):
        self._session_factory = session_factory

    def create(
        self,
    ) -> SqlAlchemyFreightOperationalAssignmentUnitOfWork:
        return SqlAlchemyFreightOperationalAssignmentUnitOfWork(
            self._session_factory
        )
