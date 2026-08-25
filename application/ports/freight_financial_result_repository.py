from typing import Protocol

from domain.models.freight_financial_result import (
    FreightFinancialResult
)


class FreightFinancialResultRepository(Protocol):

    def add(
        self,
        financial_result: FreightFinancialResult
    ) -> FreightFinancialResult:
        ...

    def get_by_freight_id(
        self,
        freight_id: int
    ) -> FreightFinancialResult | None:
        ...
