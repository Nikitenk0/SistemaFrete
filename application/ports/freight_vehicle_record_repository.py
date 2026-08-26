from typing import Protocol

from domain.models.freight_vehicle_record import (
    FreightVehicleRecord
)


class FreightVehicleRecordRepository(Protocol):

    def add(
        self,
        vehicle_record: FreightVehicleRecord
    ) -> FreightVehicleRecord:
        ...

    def get_by_id(
        self,
        freight_vehicle_record_id: int
    ) -> FreightVehicleRecord | None:
        ...

    def get_by_transport_unit_id(
        self,
        freight_transport_unit_id: int
    ) -> FreightVehicleRecord | None:
        ...

    def list_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightVehicleRecord, ...]:
        ...

    def delete_by_transport_unit_id(
        self,
        freight_transport_unit_id: int
    ) -> None:
        ...

    def get_active_by_master_vehicle(
        self,
        vehicle_id: int,
        plate: str,
        exclude_transport_unit_id: int | None = None
    ) -> FreightVehicleRecord | None:
        ...
