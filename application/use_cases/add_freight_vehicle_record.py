from datetime import (
    datetime,
    timezone
)

from application.exceptions import (
    FreightNotFoundError,
    FreightTransportUnitNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError,
    VehicleNotFoundError
)
from application.ports.freight_vehicle_record_unit_of_work import (
    FreightVehicleRecordUnitOfWorkFactory
)
from domain.models.freight import (
    FreightStatus
)
from domain.models.freight_vehicle_record import (
    FreightVehicleRecord,
    FreightVehicleType,
    get_freight_vehicle_specification
)
from domain.models.vehicle import (
    VehicleStatus
)


class AddFreightVehicleRecord:

    def __init__(
        self,
        unit_of_work_factory:
            FreightVehicleRecordUnitOfWorkFactory
    ):
        self._unit_of_work_factory = (
            unit_of_work_factory
        )

    def execute(
        self,
        freight_transport_unit_id: int,
        vehicle_type: FreightVehicleType | None = None,
        plate: str | None = None,
        created_by: int | None = None,
        vehicle_id: int | None = None
    ) -> FreightVehicleRecord:

        if freight_transport_unit_id < 1:
            raise InvalidFreightDataError(
                "freight_transport_unit_id inválido"
            )

        if created_by is not None and created_by < 1:
            raise InvalidFreightDataError(
                "created_by inválido"
            )

        with self._unit_of_work_factory.create() as unit_of_work:

            transport_unit = (
                unit_of_work.transport_units.get_by_id(
                    freight_transport_unit_id
                )
            )

            if transport_unit is None:
                raise FreightTransportUnitNotFoundError(
                    "Unidade de transporte não encontrada"
                )

            freight = (
                unit_of_work.freights.get_by_id_for_update(
                    transport_unit.freight_id
                )
            )

            if freight is None:
                raise FreightNotFoundError(
                    "Frete não encontrado"
                )

            if freight.current_status not in {
                FreightStatus.PENDING,
                FreightStatus.IN_PROGRESS
            }:
                raise InvalidFreightStateError(
                    "Frete concluído ou cancelado não aceita "
                    "novo veículo operacional"
                )

            existing_record = (
                unit_of_work.vehicle_records
                .get_by_transport_unit_id(
                    freight_transport_unit_id
                )
            )

            if existing_record is not None:
                raise InvalidFreightStateError(
                    "A unidade de transporte já possui "
                    "veículo operacional registrado"
                )

            if vehicle_id is not None:
                if vehicle_id < 1:
                    raise InvalidFreightDataError(
                        "vehicle_id inválido"
                    )

                master_vehicle = unit_of_work.vehicles.get_by_id_for_update(
                    vehicle_id
                )
                if master_vehicle is None:
                    raise VehicleNotFoundError(
                        "Veículo não encontrado"
                    )
                if master_vehicle.status != VehicleStatus.ACTIVE:
                    raise InvalidFreightStateError(
                        "Veículo inativo não pode ser usado em nova unidade operacional"
                    )

                active_vehicle_record = (
                    unit_of_work.vehicle_records
                    .get_active_by_master_vehicle(
                        vehicle_id=master_vehicle.vehicle_id,
                        plate=master_vehicle.plate
                    )
                )
                if active_vehicle_record is not None:
                    raise InvalidFreightStateError(
                        "Veículo já está vinculado a outra unidade operacional ativa"
                    )

                vehicle_type = master_vehicle.vehicle_type
                plate = master_vehicle.plate

            if vehicle_type is None or plate is None:
                raise InvalidFreightDataError(
                    "Informe o veículo operacional"
                )

            try:
                specification = (
                    get_freight_vehicle_specification(
                        vehicle_type
                    )
                )

                vehicle_record = FreightVehicleRecord(
                    freight_transport_unit_id=(
                        freight_transport_unit_id
                    ),
                    vehicle_id=vehicle_id,
                    vehicle_type=vehicle_type,
                    plate=plate,
                    axle_count=(
                        specification.axle_count
                    ),
                    pallet_capacity_min=(
                        specification.pallet_capacity_min
                    ),
                    pallet_capacity_max=(
                        specification.pallet_capacity_max
                    ),
                    payload_capacity_kg=(
                        specification.payload_capacity_kg
                    ),
                    created_at=datetime.now(
                        timezone.utc
                    ),
                    created_by=created_by
                )
            except ValueError as error:
                raise InvalidFreightDataError(
                    str(error)
                ) from error

            created_record = (
                unit_of_work.vehicle_records.add(
                    vehicle_record
                )
            )

            unit_of_work.commit()

            return created_record
