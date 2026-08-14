from dataclasses import dataclass

from domain.models.calculated_tax import CalculatedTax


@dataclass(frozen=True)
class QuoteCalculationResult:
    valor_nota: float
    geral: float
    pedagio: float
    custo: float
    subtotal: float
    impostos: tuple[CalculatedTax, ...]
    total: float

    @property
    def total_impostos(self) -> float:
        return sum(
            imposto.valor
            for imposto in self.impostos
        )