from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
)
from sqlalchemy.orm import Session

from application.exceptions import (
    TransportProviderAffiliationPersistenceError,
)
from application.ports.driver_transport_provider_affiliation_repository import (
    DriverTransportProviderAffiliationRepository,
)
from application.ports.vehicle_transport_provider_affiliation_repository import (
    VehicleTransportProviderAffiliationRepository,
)
from domain.models.driver_transport_provider_affiliation import (
    DriverTransportProviderAffiliation,
    DriverTransportProviderRole,
)
from domain.models.vehicle_transport_provider_affiliation import (
    VehicleTransportProviderAffiliation,
    VehicleTransportProviderRelation,
)
from infrastructure.persistence.sqlalchemy.models import (
    DriverTransportProviderAffiliationModel,
    VehicleTransportProviderAffiliationModel,
)


class SqlAlchemyDriverTransportProviderAffiliationRepository(
    DriverTransportProviderAffiliationRepository
):

    def __init__(self, session: Session):
        self._session = session

    def add(
        self,
        affiliation: DriverTransportProviderAffiliation,
    ) -> DriverTransportProviderAffiliation:
        model = DriverTransportProviderAffiliationModel(
            driver_id=affiliation.driver_id,
            transport_provider_id=affiliation.transport_provider_id,
            role=affiliation.role.value,
            started_at=affiliation.started_at,
            ended_at=affiliation.ended_at,
            created_by=affiliation.created_by,
            updated_by=affiliation.updated_by,
        )

        if affiliation.created_at is not None:
            model.created_at = affiliation.created_at
        if affiliation.updated_at is not None:
            model.updated_at = affiliation.updated_at

        self._session.add(model)
        try:
            self._session.flush()
            self._session.refresh(model)
        except IntegrityError as error:
            raise TransportProviderAffiliationPersistenceError(
                "Motorista já possui vínculo ativo com outro prestador"
            ) from error
        except SQLAlchemyError as error:
            raise TransportProviderAffiliationPersistenceError(
                "Não foi possível salvar vínculo do motorista"
            ) from error

        return self._to_domain(model)

    def save(
        self,
        affiliation: DriverTransportProviderAffiliation,
    ) -> DriverTransportProviderAffiliation:
        affiliation_id = (
            affiliation.driver_transport_provider_affiliation_id
        )
        if affiliation_id is None:
            raise ValueError(
                "Vínculo do motorista precisa possuir ID"
            )

        try:
            model = self._session.scalar(
                select(DriverTransportProviderAffiliationModel)
                .where(
                    DriverTransportProviderAffiliationModel
                    .driver_transport_provider_affiliation_id
                    == affiliation_id
                )
                .with_for_update()
            )
            if model is None:
                raise TransportProviderAffiliationPersistenceError(
                    "Vínculo do motorista não encontrado"
                )

            model.role = affiliation.role.value
            model.started_at = affiliation.started_at
            model.ended_at = affiliation.ended_at
            model.updated_by = affiliation.updated_by
            if affiliation.updated_at is not None:
                model.updated_at = affiliation.updated_at

            self._session.flush()
            self._session.refresh(model)
        except TransportProviderAffiliationPersistenceError:
            raise
        except SQLAlchemyError as error:
            raise TransportProviderAffiliationPersistenceError(
                "Não foi possível atualizar vínculo do motorista"
            ) from error

        return self._to_domain(model)

    def get_active_by_driver_id(
        self,
        driver_id: int,
    ) -> DriverTransportProviderAffiliation | None:
        try:
            model = self._session.scalar(
                select(DriverTransportProviderAffiliationModel)
                .where(
                    DriverTransportProviderAffiliationModel.driver_id
                    == driver_id,
                    DriverTransportProviderAffiliationModel.ended_at
                    .is_(None),
                )
            )
        except SQLAlchemyError as error:
            raise TransportProviderAffiliationPersistenceError(
                "Não foi possível consultar vínculo do motorista"
            ) from error

        return (
            self._to_domain(model)
            if model is not None
            else None
        )

    def list_by_driver_id(
        self,
        driver_id: int,
    ) -> tuple[DriverTransportProviderAffiliation, ...]:
        try:
            models = self._session.scalars(
                select(DriverTransportProviderAffiliationModel)
                .where(
                    DriverTransportProviderAffiliationModel.driver_id
                    == driver_id
                )
                .order_by(
                    DriverTransportProviderAffiliationModel.started_at,
                    DriverTransportProviderAffiliationModel
                    .driver_transport_provider_affiliation_id,
                )
            ).all()
        except SQLAlchemyError as error:
            raise TransportProviderAffiliationPersistenceError(
                "Não foi possível consultar histórico do motorista"
            ) from error

        return tuple(
            self._to_domain(model)
            for model in models
        )

    def list_active_by_provider_id(
        self,
        transport_provider_id: int,
    ) -> tuple[DriverTransportProviderAffiliation, ...]:
        try:
            models = self._session.scalars(
                select(DriverTransportProviderAffiliationModel)
                .where(
                    DriverTransportProviderAffiliationModel
                    .transport_provider_id
                    == transport_provider_id,
                    DriverTransportProviderAffiliationModel.ended_at
                    .is_(None),
                )
                .order_by(
                    DriverTransportProviderAffiliationModel.driver_id,
                    DriverTransportProviderAffiliationModel
                    .driver_transport_provider_affiliation_id,
                )
            ).all()
        except SQLAlchemyError as error:
            raise TransportProviderAffiliationPersistenceError(
                "Não foi possível consultar motoristas do prestador"
            ) from error

        return tuple(
            self._to_domain(model)
            for model in models
        )

    @staticmethod
    def _to_domain(
        model: DriverTransportProviderAffiliationModel,
    ) -> DriverTransportProviderAffiliation:
        return DriverTransportProviderAffiliation(
            driver_transport_provider_affiliation_id=(
                model.driver_transport_provider_affiliation_id
            ),
            driver_id=model.driver_id,
            transport_provider_id=model.transport_provider_id,
            role=DriverTransportProviderRole(
                model.role
            ),
            started_at=model.started_at,
            ended_at=model.ended_at,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )


class SqlAlchemyVehicleTransportProviderAffiliationRepository(
    VehicleTransportProviderAffiliationRepository
):

    def __init__(self, session: Session):
        self._session = session

    def add(
        self,
        affiliation: VehicleTransportProviderAffiliation,
    ) -> VehicleTransportProviderAffiliation:
        model = VehicleTransportProviderAffiliationModel(
            vehicle_id=affiliation.vehicle_id,
            transport_provider_id=affiliation.transport_provider_id,
            relation=affiliation.relation.value,
            started_at=affiliation.started_at,
            ended_at=affiliation.ended_at,
            created_by=affiliation.created_by,
            updated_by=affiliation.updated_by,
        )

        if affiliation.created_at is not None:
            model.created_at = affiliation.created_at
        if affiliation.updated_at is not None:
            model.updated_at = affiliation.updated_at

        self._session.add(model)
        try:
            self._session.flush()
            self._session.refresh(model)
        except IntegrityError as error:
            raise TransportProviderAffiliationPersistenceError(
                "Veículo já possui vínculo ativo com outro prestador"
            ) from error
        except SQLAlchemyError as error:
            raise TransportProviderAffiliationPersistenceError(
                "Não foi possível salvar vínculo do veículo"
            ) from error

        return self._to_domain(model)

    def save(
        self,
        affiliation: VehicleTransportProviderAffiliation,
    ) -> VehicleTransportProviderAffiliation:
        affiliation_id = (
            affiliation.vehicle_transport_provider_affiliation_id
        )
        if affiliation_id is None:
            raise ValueError(
                "Vínculo do veículo precisa possuir ID"
            )

        try:
            model = self._session.scalar(
                select(VehicleTransportProviderAffiliationModel)
                .where(
                    VehicleTransportProviderAffiliationModel
                    .vehicle_transport_provider_affiliation_id
                    == affiliation_id
                )
                .with_for_update()
            )
            if model is None:
                raise TransportProviderAffiliationPersistenceError(
                    "Vínculo do veículo não encontrado"
                )

            model.relation = affiliation.relation.value
            model.started_at = affiliation.started_at
            model.ended_at = affiliation.ended_at
            model.updated_by = affiliation.updated_by
            if affiliation.updated_at is not None:
                model.updated_at = affiliation.updated_at

            self._session.flush()
            self._session.refresh(model)
        except TransportProviderAffiliationPersistenceError:
            raise
        except SQLAlchemyError as error:
            raise TransportProviderAffiliationPersistenceError(
                "Não foi possível atualizar vínculo do veículo"
            ) from error

        return self._to_domain(model)

    def get_active_by_vehicle_id(
        self,
        vehicle_id: int,
    ) -> VehicleTransportProviderAffiliation | None:
        try:
            model = self._session.scalar(
                select(VehicleTransportProviderAffiliationModel)
                .where(
                    VehicleTransportProviderAffiliationModel.vehicle_id
                    == vehicle_id,
                    VehicleTransportProviderAffiliationModel.ended_at
                    .is_(None),
                )
            )
        except SQLAlchemyError as error:
            raise TransportProviderAffiliationPersistenceError(
                "Não foi possível consultar vínculo do veículo"
            ) from error

        return (
            self._to_domain(model)
            if model is not None
            else None
        )

    def list_by_vehicle_id(
        self,
        vehicle_id: int,
    ) -> tuple[VehicleTransportProviderAffiliation, ...]:
        try:
            models = self._session.scalars(
                select(VehicleTransportProviderAffiliationModel)
                .where(
                    VehicleTransportProviderAffiliationModel.vehicle_id
                    == vehicle_id
                )
                .order_by(
                    VehicleTransportProviderAffiliationModel.started_at,
                    VehicleTransportProviderAffiliationModel
                    .vehicle_transport_provider_affiliation_id,
                )
            ).all()
        except SQLAlchemyError as error:
            raise TransportProviderAffiliationPersistenceError(
                "Não foi possível consultar histórico do veículo"
            ) from error

        return tuple(
            self._to_domain(model)
            for model in models
        )

    def list_active_by_provider_id(
        self,
        transport_provider_id: int,
    ) -> tuple[VehicleTransportProviderAffiliation, ...]:
        try:
            models = self._session.scalars(
                select(VehicleTransportProviderAffiliationModel)
                .where(
                    VehicleTransportProviderAffiliationModel
                    .transport_provider_id
                    == transport_provider_id,
                    VehicleTransportProviderAffiliationModel.ended_at
                    .is_(None),
                )
                .order_by(
                    VehicleTransportProviderAffiliationModel.vehicle_id,
                    VehicleTransportProviderAffiliationModel
                    .vehicle_transport_provider_affiliation_id,
                )
            ).all()
        except SQLAlchemyError as error:
            raise TransportProviderAffiliationPersistenceError(
                "Não foi possível consultar veículos do prestador"
            ) from error

        return tuple(
            self._to_domain(model)
            for model in models
        )

    @staticmethod
    def _to_domain(
        model: VehicleTransportProviderAffiliationModel,
    ) -> VehicleTransportProviderAffiliation:
        return VehicleTransportProviderAffiliation(
            vehicle_transport_provider_affiliation_id=(
                model.vehicle_transport_provider_affiliation_id
            ),
            vehicle_id=model.vehicle_id,
            transport_provider_id=model.transport_provider_id,
            relation=VehicleTransportProviderRelation(
                model.relation
            ),
            started_at=model.started_at,
            ended_at=model.ended_at,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )
