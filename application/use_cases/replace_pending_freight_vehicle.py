from datetime import datetime, timezone

from application.exceptions import (
    FreightNotFoundError,
    FreightTransportUnitNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError,
    VehicleNotFoundError,
)
from application.ports.freight_vehicle_record_unit_of_work import (
    FreightVehicleRecordUnitOfWorkFactory,
)
from domain.models.freight import FreightStatus
from domain.models.freight_vehicle_record import (
    FreightVehicleRecord,
    get_freight_vehicle_specification,
)
from domain.models.vehicle import VehicleStatus


class ReplacePendingFreightVehicle:

    def __init__(self, unit_of_work_factory: FreightVehicleRecordUnitOfWorkFactory):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        freight_transport_unit_id: int,
        vehicle_id: int,
        changed_by: int | None = None,
    ) -> FreightVehicleRecord:
        if freight_transport_unit_id < 1:
            raise InvalidFreightDataError("freight_transport_unit_id inválido")
        if vehicle_id < 1:
            raise InvalidFreightDataError("vehicle_id inválido")
        if changed_by is not None and changed_by < 1:
            raise InvalidFreightDataError("changed_by inválido")

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
                raise FreightNotFoundError("Frete não encontrado")
            if freight.current_status != FreightStatus.PENDING:
                raise InvalidFreightStateError(
                    "Somente frete pendente aceita troca de veículo"
                )

            current_record = unit_of_work.vehicle_records.get_by_transport_unit_id(
                freight_transport_unit_id
            )
            if current_record is None:
                raise InvalidFreightStateError(
                    "A unidade de transporte não possui veículo para trocar"
                )

            master_vehicle = unit_of_work.vehicles.get_by_id_for_update(vehicle_id)
            if master_vehicle is None:
                raise VehicleNotFoundError("Veículo não encontrado")
            if master_vehicle.status != VehicleStatus.ACTIVE:
                raise InvalidFreightStateError(
                    "Somente veículo ativo pode substituir o veículo da unidade"
                )
            if (
                current_record.vehicle_id == master_vehicle.vehicle_id
                or current_record.plate == master_vehicle.plate
            ):
                raise InvalidFreightStateError("Selecione um veículo diferente")

            active_record = unit_of_work.vehicle_records.get_active_by_master_vehicle(
                vehicle_id=master_vehicle.vehicle_id,
                plate=master_vehicle.plate,
                exclude_transport_unit_id=freight_transport_unit_id,
            )
            if active_record is not None:
                raise InvalidFreightStateError(
                    "Veículo já está vinculado a outra unidade operacional ativa"
                )

            specification = get_freight_vehicle_specification(
                master_vehicle.vehicle_type
            )
            now = datetime.now(timezone.utc)
            replacement = FreightVehicleRecord(
                freight_transport_unit_id=freight_transport_unit_id,
                vehicle_id=master_vehicle.vehicle_id,
                vehicle_type=master_vehicle.vehicle_type,
                plate=master_vehicle.plate,
                axle_count=specification.axle_count,
                pallet_capacity_min=specification.pallet_capacity_min,
                pallet_capacity_max=specification.pallet_capacity_max,
                payload_capacity_kg=specification.payload_capacity_kg,
                created_at=now,
                created_by=changed_by,
            )

            unit_of_work.vehicle_records.delete_by_transport_unit_id(
                freight_transport_unit_id
            )
            created = unit_of_work.vehicle_records.add(replacement)
            unit_of_work.commit()
            return created
