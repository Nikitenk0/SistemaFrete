from typing import Protocol

from domain.models.freight import (
    Freight
)


class FreightRepository(Protocol):

    def add(
        self,
        freight: Freight
    ) -> Freight:
        ...

    def get_by_id(
        self,
        freight_id: int
    ) -> Freight | None:
        ...

    def get_by_primary_quote_id(
        self,
        primary_quote_id: int
    ) -> Freight | None:
        ...
