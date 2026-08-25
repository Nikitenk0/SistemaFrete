from application.exceptions import (
    InvalidVehicleDataError,
    VehicleNotFoundError
)
from application.ports.vehicle_unit_of_work import (
    VehicleUnitOfWorkFactory
)
from domain.models.vehicle import (
    Vehicle
)


class GetVehicle:

    def __init__(
        self,
        unit_of_work_factory: VehicleUnitOfWorkFactory
    ):
        self._unit_of_work_factory = (
            unit_of_work_factory
        )

    def execute(
        self,
        vehicle_id: int
    ) -> Vehicle:

        if vehicle_id < 1:
            raise InvalidVehicleDataError(
                "vehicle_id inválido"
            )

        with (
            self._unit_of_work_factory.create()
            as unit_of_work
        ):
            vehicle = unit_of_work.vehicles.get_by_id(
                vehicle_id
            )

        if vehicle is None:
            raise VehicleNotFoundError(
                "Veículo não encontrado"
            )

        return vehicle
