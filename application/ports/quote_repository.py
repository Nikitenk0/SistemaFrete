from typing import Protocol

from domain.models.quote import (
    Quote
)


class QuoteRepository(Protocol):

    def add(
        self,
        quote: Quote
    ) -> Quote:
        ...

    def save(
        self,
        quote: Quote
    ) -> Quote:
        ...

    def get_by_id(
        self,
        quote_id: int
    ) -> Quote | None:
        ...

    def get_by_id_for_update(
        self,
        quote_id: int
    ) -> Quote | None:
        ...

    def get_by_number(
        self,
        quote_number: str
    ) -> Quote | None:
        ...