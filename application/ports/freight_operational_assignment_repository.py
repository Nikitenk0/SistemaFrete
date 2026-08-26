from typing import Protocol

from domain.models.freight_operational_assignment import (
    FreightOperationalAssignment,
)


class FreightOperationalAssignmentRepository(Protocol):

    def add(
        self,
        assignment: FreightOperationalAssignment,
    ) -> FreightOperationalAssignment:
        ...

    def get_by_driver_assignment_id(
        self,
        freight_driver_assignment_id: int,
    ) -> FreightOperationalAssignment | None:
        ...

    def list_by_transport_unit_id(
        self,
        freight_transport_unit_id: int,
    ) -> tuple[FreightOperationalAssignment, ...]:
        ...
