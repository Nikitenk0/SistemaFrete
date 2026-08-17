from typing import Protocol

from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)
from domain.models.route_result import RouteResult


class QuotePdfGenerator(Protocol):

    def generate(
        self,
        route_result: RouteResult,
        quote_result: QuoteCalculationResult,
        axle_count: int,
        include_return_trip: bool,
        path: str
    ) -> None:
        ...