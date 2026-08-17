from dataclasses import dataclass

from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)
from application.dtos.route_result import RouteResult


@dataclass(frozen=True)
class ClosedLoadQuoteResult:
    route_result: RouteResult
    quote_result: QuoteCalculationResult