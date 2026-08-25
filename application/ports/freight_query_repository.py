from typing import Protocol

from application.dtos.freight_query import (
    FreightDetails,
    FreightListItem,
    FreightQueryFilters,
)


class FreightQueryRepository(Protocol):

    def list(
        self,
        filters: FreightQueryFilters,
    ) -> tuple[FreightListItem, ...]:
        ...

    def get_by_id(
        self,
        freight_id: int,
    ) -> FreightDetails | None:
        ...
