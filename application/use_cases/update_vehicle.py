from dataclasses import replace
from datetime import (
    datetime,
    timezone
)

from application.exceptions import (
    InvalidVehicleDataError,
    VehicleAlreadyExistsError,
    VehicleNotFoundError
)
from application.ports.vehicle_unit_of_work import (
    VehicleUnitOfWorkFactory
)
from domain.models.vehicle import (
    Vehicle,
    VehicleStatus,
    VehicleType,
    normalize_vehicle_plate
)


class UpdateVehicle:

    def __init__(
        self,
        unit_of_work_factory: VehicleUnitOfWorkFactory
    ):
        self._unit_of_work_factory = (
            unit_of_work_factory
        )

    def execute(
        self,
        vehicle_id: int,
        plate: str,
        vehicle_type: VehicleType,
        status: VehicleStatus,
        updated_by: int | None = None
    ) -> Vehicle:

        if vehicle_id < 1:
            raise InvalidVehicleDataError(
                "vehicle_id inválido"
            )

        if updated_by is not None and updated_by < 1:
            raise InvalidVehicleDataError(
                "updated_by inválido"
            )

        try:
            normalized_plate = normalize_vehicle_plate(
                plate
            )
            normalized_vehicle_type = VehicleType(
                vehicle_type
            )
            normalized_status = VehicleStatus(
                status
            )
        except (ValueError, TypeError) as error:
            raise InvalidVehicleDataError(
                str(error)
            ) from error

        with (
            self._unit_of_work_factory.create()
            as unit_of_work
        ):

            current_vehicle = (
                unit_of_work.vehicles.get_by_id_for_update(
                    vehicle_id
                )
            )

            if current_vehicle is None:
                raise VehicleNotFoundError(
                    "Veículo não encontrado"
                )

            vehicle_with_plate = (
                unit_of_work.vehicles.get_by_plate(
                    normalized_plate
                )
            )

            if (
                vehicle_with_plate is not None
                and vehicle_with_plate.vehicle_id
                != vehicle_id
            ):
                raise VehicleAlreadyExistsError(
                    "Placa já cadastrada para outro veículo"
                )

            try:
                updated_vehicle = replace(
                    current_vehicle,
                    plate=normalized_plate,
                    vehicle_type=normalized_vehicle_type,
                    status=normalized_status,
                    updated_at=datetime.now(
                        timezone.utc
                    ),
                    updated_by=updated_by
                )
            except ValueError as error:
                raise InvalidVehicleDataError(
                    str(error)
                ) from error

            saved_vehicle = (
                unit_of_work.vehicles.save(
                    updated_vehicle
                )
            )

            unit_of_work.commit()

            return saved_vehicle
