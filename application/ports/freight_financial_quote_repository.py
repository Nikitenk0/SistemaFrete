from typing import Protocol

from domain.models.quote import Quote


class FreightFinancialQuoteRepository(Protocol):

    def list_by_freight_id_for_update(
        self,
        freight_id: int
    ) -> tuple[Quote, ...]:
        ...
