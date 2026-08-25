from application.exceptions import (
    InvalidVehicleDataError
)
from application.ports.vehicle_unit_of_work import (
    VehicleUnitOfWorkFactory
)
from domain.models.vehicle import (
    Vehicle,
    VehicleStatus,
    VehicleType
)


class SearchVehicles:

    def __init__(
        self,
        unit_of_work_factory: VehicleUnitOfWorkFactory
    ):
        self._unit_of_work_factory = (
            unit_of_work_factory
        )

    def execute(
        self,
        query: str = "",
        status: VehicleStatus | None = None,
        vehicle_type: VehicleType | None = None,
        limit: int = 100
    ) -> tuple[Vehicle, ...]:

        if limit < 1 or limit > 200:
            raise InvalidVehicleDataError(
                "limit inválido"
            )

        try:
            normalized_status = (
                VehicleStatus(status)
                if status is not None
                else None
            )
            normalized_vehicle_type = (
                VehicleType(vehicle_type)
                if vehicle_type is not None
                else None
            )
        except (ValueError, TypeError) as error:
            raise InvalidVehicleDataError(
                "Filtro de veículo inválido"
            ) from error

        with (
            self._unit_of_work_factory.create()
            as unit_of_work
        ):
            return unit_of_work.vehicles.search(
                query=query,
                status=normalized_status,
                vehicle_type=normalized_vehicle_type,
                limit=limit
            )
