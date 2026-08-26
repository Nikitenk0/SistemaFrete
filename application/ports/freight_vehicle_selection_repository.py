from typing import Protocol

from domain.models.vehicle import Vehicle


class FreightVehicleSelectionRepository(Protocol):

    def search_available(
        self,
        query: str = "",
        limit: int = 200,
    ) -> tuple[Vehicle, ...]:
        ...
