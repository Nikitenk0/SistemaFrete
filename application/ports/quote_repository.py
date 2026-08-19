from typing import Protocol

from domain.models.quote import Quote


class QuoteRepository(Protocol):

    def add(
        self,
        quote: Quote
    ) -> Quote:
        ...

    def get_by_id(
        self,
        quote_id: int
    ) -> Quote | None:
        ...