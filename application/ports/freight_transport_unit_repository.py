from typing import Protocol

from domain.models.freight_transport_unit import (
    FreightTransportUnit
)


class FreightTransportUnitRepository(Protocol):

    def add(
        self,
        transport_unit: FreightTransportUnit
    ) -> FreightTransportUnit:
        ...

    def get_by_id(
        self,
        freight_transport_unit_id: int
    ) -> FreightTransportUnit | None:
        ...

    def list_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightTransportUnit, ...]:
        ...

    def count_by_freight_id(
        self,
        freight_id: int
    ) -> int:
        ...

    def delete_by_id(
        self,
        freight_transport_unit_id: int
    ) -> None:
        ...
