from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal

from application.exceptions import (
    DriverNotFoundError,
    FreightNotFoundError,
    FreightTransportUnitNotFoundError,
    InvalidDriverStateError,
    InvalidFreightDataError,
    InvalidFreightStateError,
    InvalidTransportProviderStateError,
    TransportProviderNotFoundError,
    VehicleNotFoundError,
)
from application.ports.freight_operational_assignment_unit_of_work import (
    FreightOperationalAssignmentUnitOfWorkFactory,
)
from domain.models.driver import DriverStatus
from domain.models.freight import FreightStatus
from domain.models.freight_driver_assignment import (
    FreightDriverAssignment,
)
from domain.models.freight_operational_assignment import (
    FreightOperationalAssignment,
)
from domain.models.freight_vehicle_record import (
    FreightVehicleRecord,
    get_freight_vehicle_specification,
)
from domain.models.transport_provider import (
    TransportProviderStatus,
)
from domain.models.vehicle import VehicleStatus


class ReplaceInProgressFreightOperationalAssignment:
    """Troca atomica do conjunto operacional durante a viagem.

    O parametro actual_transport_amount representa o valor realizado
    pelo conjunto/prestador no trecho encerrado. Por compatibilidade
    com o modelo atual, esse valor ainda e persistido no campo legado
    actual_driver_amount da participacao do motorista.
    """

    def __init__(
        self,
        unit_of_work_factory: FreightOperationalAssignmentUnitOfWorkFactory,
    ):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        freight_transport_unit_id: int,
        transport_provider_id: int,
        driver_id: int,
        vehicle_id: int,
        actual_transport_amount: Decimal,
        switched_at: datetime | None = None,
        changed_by: int | None = None,
    ) -> FreightOperationalAssignment:
        if freight_transport_unit_id < 1:
            raise InvalidFreightDataError(
                "freight_transport_unit_id invalido"
            )
        if transport_provider_id < 1:
            raise InvalidFreightDataError(
                "transport_provider_id invalido"
            )
        if driver_id < 1:
            raise InvalidFreightDataError(
                "driver_id invalido"
            )
        if vehicle_id < 1:
            raise InvalidFreightDataError(
                "vehicle_id invalido"
            )
        if changed_by is not None and changed_by < 1:
            raise InvalidFreightDataError(
                "changed_by invalido"
            )

        switch_time = switched_at or datetime.now(
            timezone.utc
        )
        now = datetime.now(
            timezone.utc
        )

        with self._unit_of_work_factory.create() as unit_of_work:
            transport_unit = unit_of_work.transport_units.get_by_id(
                freight_transport_unit_id
            )
            if transport_unit is None:
                raise FreightTransportUnitNotFoundError(
                    "Unidade de transporte nao encontrada"
                )

            freight = unit_of_work.freights.get_by_id_for_update(
                transport_unit.freight_id
            )
            if freight is None:
                raise FreightNotFoundError(
                    "Frete nao encontrado"
                )

            if freight.current_status != FreightStatus.IN_PROGRESS:
                raise InvalidFreightStateError(
                    "Somente frete em andamento aceita "
                    "troca de conjunto operacional"
                )

            current_assignment = (
                unit_of_work.driver_assignments
                .get_active_by_transport_unit_id(
                    freight_transport_unit_id
                )
            )
            if current_assignment is None:
                raise InvalidFreightStateError(
                    "Unidade nao possui participacao ativa "
                    "para encerrar"
                )

            current_context = (
                unit_of_work.operational_assignments
                .get_by_driver_assignment_id(
                    current_assignment.freight_driver_assignment_id
                )
            )
            if current_context is None:
                raise InvalidFreightStateError(
                    "Reconheca o conjunto operacional atual "
                    "antes de realizar a troca"
                )

            current_vehicle_record = (
                unit_of_work.vehicle_records
                .get_by_transport_unit_id(
                    freight_transport_unit_id
                )
            )
            if (
                current_vehicle_record is None
                or current_vehicle_record.vehicle_id is None
            ):
                raise InvalidFreightStateError(
                    "Unidade nao possui veiculo mestre atual"
                )

            provider = unit_of_work.providers.get_by_id_for_update(
                transport_provider_id
            )
            if provider is None:
                raise TransportProviderNotFoundError(
                    "Prestador de transporte nao encontrado"
                )
            if provider.status != TransportProviderStatus.ACTIVE:
                raise InvalidTransportProviderStateError(
                    "Prestador inativo nao pode assumir o trecho"
                )

            driver = unit_of_work.drivers.get_by_id_for_update(
                driver_id
            )
            if driver is None:
                raise DriverNotFoundError(
                    "Motorista nao encontrado"
                )
            if driver.status != DriverStatus.ACTIVE:
                raise InvalidDriverStateError(
                    "Motorista inativo nao pode assumir o trecho"
                )

            vehicle = unit_of_work.vehicles.get_by_id_for_update(
                vehicle_id
            )
            if vehicle is None:
                raise VehicleNotFoundError(
                    "Veiculo nao encontrado"
                )
            if vehicle.status != VehicleStatus.ACTIVE:
                raise InvalidFreightStateError(
                    "Veiculo inativo nao pode assumir o trecho"
                )

            driver_affiliation = (
                unit_of_work.driver_affiliations
                .get_active_by_driver_id(
                    driver_id
                )
            )
            if (
                driver_affiliation is None
                or driver_affiliation.transport_provider_id
                != transport_provider_id
            ):
                raise InvalidTransportProviderStateError(
                    "Motorista nao possui vinculo ativo "
                    "com o prestador selecionado"
                )

            vehicle_affiliation = (
                unit_of_work.vehicle_affiliations
                .get_active_by_vehicle_id(
                    vehicle_id
                )
            )
            if (
                vehicle_affiliation is None
                or vehicle_affiliation.transport_provider_id
                != transport_provider_id
            ):
                raise InvalidTransportProviderStateError(
                    "Veiculo nao possui vinculo ativo "
                    "com o prestador selecionado"
                )

            same_driver = (
                current_assignment.driver_id
                == driver_id
            )
            same_vehicle = (
                current_vehicle_record.vehicle_id
                == vehicle_id
            )

            if same_driver and same_vehicle:
                raise InvalidFreightStateError(
                    "Selecione um conjunto operacional diferente"
                )

            if not same_driver and same_vehicle:
                raise InvalidFreightStateError(
                    "Ao trocar o motorista, selecione tambem "
                    "outro veiculo"
                )

            active_driver_assignment = (
                unit_of_work.driver_assignments
                .get_active_by_driver_id(
                    driver_id
                )
            )
            if (
                active_driver_assignment is not None
                and active_driver_assignment
                .freight_driver_assignment_id
                != current_assignment.freight_driver_assignment_id
            ):
                raise InvalidFreightStateError(
                    "Motorista ja possui participacao "
                    "operacional ativa"
                )

            active_vehicle_record = (
                unit_of_work.vehicle_records
                .get_active_by_master_vehicle(
                    vehicle_id=vehicle.vehicle_id,
                    plate=vehicle.plate,
                    exclude_transport_unit_id=(
                        freight_transport_unit_id
                    ),
                )
            )
            if active_vehicle_record is not None:
                raise InvalidFreightStateError(
                    "Veiculo ja esta vinculado a outra "
                    "unidade operacional ativa"
                )

            try:
                finished_assignment = replace(
                    current_assignment,
                    ended_at=switch_time,
                    actual_driver_amount=actual_transport_amount,
                    updated_at=now,
                    updated_by=changed_by,
                )
            except (TypeError, ValueError) as error:
                raise InvalidFreightDataError(
                    str(error)
                ) from error

            unit_of_work.driver_assignments.save(
                finished_assignment
            )

            specification = get_freight_vehicle_specification(
                vehicle.vehicle_type
            )

            try:
                replacement_vehicle = FreightVehicleRecord(
                    freight_transport_unit_id=(
                        freight_transport_unit_id
                    ),
                    vehicle_id=vehicle.vehicle_id,
                    vehicle_type=vehicle.vehicle_type,
                    plate=vehicle.plate,
                    axle_count=specification.axle_count,
                    pallet_capacity_min=(
                        specification.pallet_capacity_min
                    ),
                    pallet_capacity_max=(
                        specification.pallet_capacity_max
                    ),
                    payload_capacity_kg=(
                        specification.payload_capacity_kg
                    ),
                    created_at=now,
                    created_by=changed_by,
                )
            except (TypeError, ValueError) as error:
                raise InvalidFreightDataError(
                    str(error)
                ) from error

            unit_of_work.vehicle_records.delete_by_transport_unit_id(
                freight_transport_unit_id
            )
            unit_of_work.vehicle_records.add(
                replacement_vehicle
            )

            try:
                next_assignment = FreightDriverAssignment(
                    freight_transport_unit_id=(
                        freight_transport_unit_id
                    ),
                    driver_id=driver_id,
                    started_at=switch_time,
                    created_at=now,
                    created_by=changed_by,
                    updated_at=now,
                    updated_by=changed_by,
                )
            except (TypeError, ValueError) as error:
                raise InvalidFreightDataError(
                    str(error)
                ) from error

            created_assignment = (
                unit_of_work.driver_assignments.add(
                    next_assignment
                )
            )

            provider_name = (
                provider.trade_name
                or provider.legal_name
            )

            try:
                next_context = FreightOperationalAssignment(
                    freight_driver_assignment_id=(
                        created_assignment
                        .freight_driver_assignment_id
                    ),
                    transport_provider_id=(
                        transport_provider_id
                    ),
                    vehicle_id=vehicle.vehicle_id,
                    provider_name_snapshot=provider_name,
                    provider_tax_document_snapshot=(
                        provider.tax_document
                    ),
                    driver_name_snapshot=driver.name,
                    driver_cpf_snapshot=driver.cpf,
                    vehicle_plate_snapshot=vehicle.plate,
                    vehicle_type_snapshot=(
                        vehicle.vehicle_type
                    ),
                    created_at=now,
                    created_by=changed_by,
                )
            except (TypeError, ValueError) as error:
                raise InvalidFreightDataError(
                    str(error)
                ) from error

            created_context = (
                unit_of_work.operational_assignments.add(
                    next_context
                )
            )

            unit_of_work.commit()
            return created_context
