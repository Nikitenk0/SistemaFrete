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
