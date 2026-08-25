from typing import Protocol

from domain.models.freight_driver_assignment import (
    FreightDriverAssignment
)


class FreightDriverAssignmentRepository(Protocol):

    def add(
        self,
        assignment: FreightDriverAssignment
    ) -> FreightDriverAssignment:
        ...

    def save(
        self,
        assignment: FreightDriverAssignment
    ) -> FreightDriverAssignment:
        ...

    def get_by_id(
        self,
        freight_driver_assignment_id: int
    ) -> FreightDriverAssignment | None:
        ...

    def get_active_by_transport_unit_id(
        self,
        freight_transport_unit_id: int
    ) -> FreightDriverAssignment | None:
        ...

    def get_active_by_driver_id(
        self,
        driver_id: int
    ) -> FreightDriverAssignment | None:
        ...

    def list_by_transport_unit_id(
        self,
        freight_transport_unit_id: int
    ) -> tuple[FreightDriverAssignment, ...]:
        ...

    def list_active_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightDriverAssignment, ...]:
        ...

    def list_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightDriverAssignment, ...]:
        ...
