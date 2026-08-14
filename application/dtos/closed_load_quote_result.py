from dataclasses import dataclass

from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)
from domain.models.route_result import RouteResult


@dataclass(frozen=True)
class ClosedLoadQuoteResult:
    rota: RouteResult
    orcamento: QuoteCalculationResult