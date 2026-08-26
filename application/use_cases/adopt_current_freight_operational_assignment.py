from datetime import datetime, timezone

from application.exceptions import (
    FreightNotFoundError,
    FreightTransportUnitNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError,
    InvalidTransportProviderStateError,
)
from application.ports.freight_operational_assignment_unit_of_work import (
    FreightOperationalAssignmentUnitOfWorkFactory,
)
from domain.models.freight import FreightStatus
from domain.models.freight_operational_assignment import (
    FreightOperationalAssignment,
)


class AdoptCurrentFreightOperationalAssignment:

    def __init__(
        self,
        unit_of_work_factory: FreightOperationalAssignmentUnitOfWorkFactory,
    ):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        freight_transport_unit_id: int,
        created_by: int | None = None,
    ) -> FreightOperationalAssignment:
        if freight_transport_unit_id < 1:
            raise InvalidFreightDataError(
                "freight_transport_unit_id inválido"
            )

        if created_by is not None and created_by < 1:
            raise InvalidFreightDataError(
                "created_by inválido"
            )

        with self._unit_of_work_factory.create() as unit_of_work:
            transport_unit = unit_of_work.transport_units.get_by_id(
                freight_transport_unit_id
            )
            if transport_unit is None:
                raise FreightTransportUnitNotFoundError(
                    "Unidade de transporte não encontrada"
                )

            freight = unit_of_work.freights.get_by_id_for_update(
                transport_unit.freight_id
            )
            if freight is None:
                raise FreightNotFoundError(
                    "Frete não encontrado"
                )

            if freight.current_status not in {
                FreightStatus.PENDING,
                FreightStatus.IN_PROGRESS,
            }:
                raise InvalidFreightStateError(
                    "Somente frete pendente ou em andamento "
                    "aceita reconhecimento do conjunto atual"
                )

            driver_assignment = (
                unit_of_work.driver_assignments
                .get_active_by_transport_unit_id(
                    freight_transport_unit_id
                )
            )
            if driver_assignment is None:
                raise InvalidFreightStateError(
                    "Unidade não possui motorista ativo"
                )

            existing = (
                unit_of_work.operational_assignments
                .get_by_driver_assignment_id(
                    driver_assignment.freight_driver_assignment_id
                )
            )
            if existing is not None:
                return existing

            vehicle_record = (
                unit_of_work.vehicle_records
                .get_by_transport_unit_id(
                    freight_transport_unit_id
                )
            )
            if (
                vehicle_record is None
                or vehicle_record.vehicle_id is None
            ):
                raise InvalidFreightStateError(
                    "Unidade não possui veículo mestre reconhecível"
                )

            driver_affiliation = (
                unit_of_work.driver_affiliations
                .get_active_by_driver_id(
                    driver_assignment.driver_id
                )
            )
            if driver_affiliation is None:
                raise InvalidTransportProviderStateError(
                    "Motorista ativo não possui vínculo com prestador"
                )

            vehicle_affiliation = (
                unit_of_work.vehicle_affiliations
                .get_active_by_vehicle_id(
                    vehicle_record.vehicle_id
                )
            )
            if vehicle_affiliation is None:
                raise InvalidTransportProviderStateError(
                    "Veículo atual não possui vínculo com prestador"
                )

            if (
                driver_affiliation.transport_provider_id
                != vehicle_affiliation.transport_provider_id
            ):
                raise InvalidTransportProviderStateError(
                    "Motorista e veículo atuais pertencem "
                    "a prestadores diferentes"
                )

            provider_id = (
                driver_affiliation.transport_provider_id
            )
            provider = unit_of_work.providers.get_by_id(
                provider_id
            )
            if provider is None:
                raise InvalidTransportProviderStateError(
                    "Prestador do conjunto atual não foi encontrado"
                )

            driver = unit_of_work.drivers.get_by_id(
                driver_assignment.driver_id
            )
            if driver is None:
                raise InvalidFreightStateError(
                    "Motorista da participação não foi encontrado"
                )

            vehicle = unit_of_work.vehicles.get_by_id(
                vehicle_record.vehicle_id
            )
            if vehicle is None:
                raise InvalidFreightStateError(
                    "Veículo mestre da unidade não foi encontrado"
                )

            provider_name = (
                provider.trade_name
                or provider.legal_name
            )

            try:
                context = FreightOperationalAssignment(
                    freight_driver_assignment_id=(
                        driver_assignment.freight_driver_assignment_id
                    ),
                    transport_provider_id=provider_id,
                    vehicle_id=vehicle.vehicle_id,
                    provider_name_snapshot=provider_name,
                    provider_tax_document_snapshot=(
                        provider.tax_document
                    ),
                    driver_name_snapshot=driver.name,
                    driver_cpf_snapshot=driver.cpf,
                    vehicle_plate_snapshot=(
                        vehicle_record.plate
                    ),
                    vehicle_type_snapshot=(
                        vehicle_record.vehicle_type
                    ),
                    created_at=datetime.now(timezone.utc),
                    created_by=created_by,
                )
            except ValueError as error:
                raise InvalidFreightDataError(
                    str(error)
                ) from error

            created = unit_of_work.operational_assignments.add(
                context
            )
            unit_of_work.commit()
            return created
