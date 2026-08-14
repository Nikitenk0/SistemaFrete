from typing import Protocol

from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)
from domain.models.route_result import RouteResult


class QuotePdfGenerator(Protocol):

    def generate(
        self,
        resultado_rota: RouteResult,
        resultado_orcamento: QuoteCalculationResult,
        quantidade_eixos: int,
        calcular_volta: bool,
        caminho: str
    ) -> None:
        ...