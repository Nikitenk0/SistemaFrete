from dataclasses import replace
from datetime import datetime, timezone

from application.exceptions import (
    InvalidTransportProviderDataError,
    InvalidTransportProviderStateError,
    InvalidVehicleDataError,
    TransportProviderNotFoundError,
    VehicleNotFoundError,
)
from application.ports.transport_provider_unit_of_work import (
    TransportProviderUnitOfWorkFactory,
)
from domain.models.transport_provider import (
    TransportProviderStatus,
)
from domain.models.vehicle import VehicleStatus
from domain.models.vehicle_transport_provider_affiliation import (
    VehicleTransportProviderAffiliation,
    VehicleTransportProviderRelation,
)


class SetVehicleTransportProviderAffiliation:

    def __init__(
        self,
        unit_of_work_factory: TransportProviderUnitOfWorkFactory,
    ):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        vehicle_id: int,
        transport_provider_id: int,
        relation: VehicleTransportProviderRelation,
        changed_at: datetime | None = None,
        changed_by: int | None = None,
    ) -> VehicleTransportProviderAffiliation:
        if vehicle_id < 1:
            raise InvalidVehicleDataError(
                "vehicle_id inválido"
            )

        if transport_provider_id < 1:
            raise InvalidTransportProviderDataError(
                "transport_provider_id inválido"
            )

        if changed_by is not None and changed_by < 1:
            raise InvalidTransportProviderDataError(
                "changed_by inválido"
            )

        now = changed_at or datetime.now(timezone.utc)

        with self._unit_of_work_factory.create() as unit_of_work:
            vehicle = unit_of_work.vehicles.get_by_id_for_update(
                vehicle_id
            )
            if vehicle is None:
                raise VehicleNotFoundError(
                    "Veículo não encontrado"
                )

            if vehicle.status != VehicleStatus.ACTIVE:
                raise InvalidTransportProviderStateError(
                    "Veículo inativo não pode receber novo vínculo"
                )

            provider = unit_of_work.providers.get_by_id_for_update(
                transport_provider_id
            )
            if provider is None:
                raise TransportProviderNotFoundError(
                    "Prestador de transporte não encontrado"
                )

            if provider.status != TransportProviderStatus.ACTIVE:
                raise InvalidTransportProviderStateError(
                    "Prestador inativo não pode receber novo vínculo"
                )

            try:
                relation = VehicleTransportProviderRelation(
                    relation
                )
            except (TypeError, ValueError) as error:
                raise InvalidTransportProviderDataError(
                    "relation inválida"
                ) from error

            current = (
                unit_of_work.vehicle_affiliations
                .get_active_by_vehicle_id(
                    vehicle_id
                )
            )

            if (
                current is not None
                and current.transport_provider_id
                == transport_provider_id
                and current.relation == relation
            ):
                return current

            if current is not None:
                ended = replace(
                    current,
                    ended_at=now,
                    updated_at=now,
                    updated_by=changed_by,
                )
                unit_of_work.vehicle_affiliations.save(
                    ended
                )

            try:
                affiliation = VehicleTransportProviderAffiliation(
                    vehicle_id=vehicle_id,
                    transport_provider_id=transport_provider_id,
                    relation=relation,
                    started_at=now,
                    created_at=now,
                    created_by=changed_by,
                    updated_at=now,
                    updated_by=changed_by,
                )
            except (TypeError, ValueError) as error:
                raise InvalidTransportProviderDataError(
                    str(error)
                ) from error

            created = unit_of_work.vehicle_affiliations.add(
                affiliation
            )
            unit_of_work.commit()
            return created
