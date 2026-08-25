from typing import Protocol

from application.dtos.driver_query import (
    DriverListItem
)
from domain.models.driver import (
    DriverStatus
)


class DriverQueryRepository(Protocol):

    def list(
        self,
        query: str = "",
        status: DriverStatus | None = None,
        limit: int = 100
    ) -> tuple[DriverListItem, ...]:
        ...
