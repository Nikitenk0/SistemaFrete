from application.exceptions import InvalidVehicleDataError
from application.ports.freight_vehicle_selection_repository import (
    FreightVehicleSelectionRepository,
)
from domain.models.vehicle import Vehicle


class SearchAvailableFreightVehicles:

    def __init__(self, repository: FreightVehicleSelectionRepository):
        self._repository = repository

    def execute(
        self,
        query: str = "",
        limit: int = 200,
    ) -> tuple[Vehicle, ...]:
        if not isinstance(query, str):
            raise InvalidVehicleDataError("query inválida")
        if limit < 1 or limit > 200:
            raise InvalidVehicleDataError("limit inválido")
        return self._repository.search_available(
            query=query.strip(),
            limit=limit,
        )
