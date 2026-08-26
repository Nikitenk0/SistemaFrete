from typing import Protocol

from application.dtos.freight_driver_selection import (
    FreightDriverSelectionItem,
)


class FreightDriverSelectionRepository(Protocol):

    def search_available(
        self,
        query: str,
        limit: int = 20,
    ) -> tuple[FreightDriverSelectionItem, ...]:
        ...
