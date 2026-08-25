from application.exceptions import (
    InvalidVehicleDataError,
    VehicleAlreadyExistsError
)
from application.ports.vehicle_unit_of_work import (
    VehicleUnitOfWorkFactory
)
from domain.models.vehicle import (
    Vehicle,
    VehicleStatus,
    VehicleType
)


class CreateVehicle:

    def __init__(
        self,
        unit_of_work_factory: VehicleUnitOfWorkFactory
    ):
        self._unit_of_work_factory = (
            unit_of_work_factory
        )

    def execute(
        self,
        plate: str,
        vehicle_type: VehicleType,
        status: VehicleStatus = VehicleStatus.ACTIVE,
        created_by: int | None = None
    ) -> Vehicle:

        try:
            vehicle = Vehicle(
                plate=plate,
                vehicle_type=vehicle_type,
                status=status,
                created_by=created_by,
                updated_by=created_by
            )
        except ValueError as error:
            raise InvalidVehicleDataError(
                str(error)
            ) from error

        with (
            self._unit_of_work_factory.create()
            as unit_of_work
        ):

            existing_vehicle = (
                unit_of_work.vehicles.get_by_plate(
                    vehicle.plate
                )
            )

            if existing_vehicle is not None:
                raise VehicleAlreadyExistsError(
                    "Placa já cadastrada para outro veículo"
                )

            created_vehicle = (
                unit_of_work.vehicles.add(
                    vehicle
                )
            )

            unit_of_work.commit()

            return created_vehicle
