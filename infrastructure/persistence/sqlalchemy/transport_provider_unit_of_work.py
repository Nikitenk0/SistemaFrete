from types import TracebackType

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from application.exceptions import (
    TransportProviderPersistenceError,
)
from application.ports.driver_repository import DriverRepository
from application.ports.driver_transport_provider_affiliation_repository import (
    DriverTransportProviderAffiliationRepository,
)
from application.ports.transport_provider_repository import (
    TransportProviderRepository,
)
from application.ports.transport_provider_unit_of_work import (
    TransportProviderUnitOfWork,
)
from application.ports.vehicle_repository import VehicleRepository
from application.ports.vehicle_transport_provider_affiliation_repository import (
    VehicleTransportProviderAffiliationRepository,
)
from infrastructure.persistence.sqlalchemy.driver_repository import (
    SqlAlchemyDriverRepository,
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


class SqlAlchemyTransportProviderUnitOfWork(
    TransportProviderUnitOfWork
):

    def __init__(
        self,
        session_factory: sessionmaker[Session],
    ):
        self._session_factory = session_factory
        self._session: Session | None = None
        self._providers: TransportProviderRepository | None = None
        self._driver_affiliations: (
            DriverTransportProviderAffiliationRepository | None
        ) = None
        self._vehicle_affiliations: (
            VehicleTransportProviderAffiliationRepository | None
        ) = None
        self._drivers: DriverRepository | None = None
        self._vehicles: VehicleRepository | None = None

    @property
    def providers(self) -> TransportProviderRepository:
        if self._providers is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return self._providers

    @property
    def driver_affiliations(
        self,
    ) -> DriverTransportProviderAffiliationRepository:
        if self._driver_affiliations is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return self._driver_affiliations

    @property
    def vehicle_affiliations(
        self,
    ) -> VehicleTransportProviderAffiliationRepository:
        if self._vehicle_affiliations is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return self._vehicle_affiliations

    @property
    def drivers(self) -> DriverRepository:
        if self._drivers is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return self._drivers

    @property
    def vehicles(self) -> VehicleRepository:
        if self._vehicles is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )
        return self._vehicles

    def __enter__(
        self,
    ) -> "SqlAlchemyTransportProviderUnitOfWork":
        self._session = self._session_factory()
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
            self._providers = None
            self._driver_affiliations = None
            self._vehicle_affiliations = None
            self._drivers = None
            self._vehicles = None

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError(
                "Unit of Work não iniciado"
            )

        try:
            self._session.commit()
        except SQLAlchemyError as error:
            self._session.rollback()
            raise TransportProviderPersistenceError(
                "Não foi possível confirmar a operação com o prestador"
            ) from error

    def rollback(self) -> None:
        if self._session is not None:
            self._session.rollback()


class SqlAlchemyTransportProviderUnitOfWorkFactory:

    def __init__(
        self,
        session_factory: sessionmaker[Session],
    ):
        self._session_factory = session_factory

    def create(
        self,
    ) -> SqlAlchemyTransportProviderUnitOfWork:
        return SqlAlchemyTransportProviderUnitOfWork(
            self._session_factory
        )
