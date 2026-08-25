from typing import Protocol

from domain.models.vehicle import (
    Vehicle,
    VehicleStatus,
    VehicleType
)


class VehicleRepository(Protocol):

    def add(
        self,
        vehicle: Vehicle
    ) -> Vehicle:
        ...

    def save(
        self,
        vehicle: Vehicle
    ) -> Vehicle:
        ...

    def get_by_id(
        self,
        vehicle_id: int
    ) -> Vehicle | None:
        ...

    def get_by_id_for_update(
        self,
        vehicle_id: int
    ) -> Vehicle | None:
        ...

    def get_by_plate(
        self,
        plate: str
    ) -> Vehicle | None:
        ...

    def search(
        self,
        query: str = "",
        status: VehicleStatus | None = None,
        vehicle_type: VehicleType | None = None,
        limit: int = 100
    ) -> tuple[Vehicle, ...]:
        ...
