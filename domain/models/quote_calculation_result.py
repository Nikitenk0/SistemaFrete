from dataclasses import dataclass
from decimal import Decimal

from domain.models.calculated_tax import CalculatedTax


@dataclass(frozen=True)
class QuoteCalculationResult:
    valor_nota: Decimal
    geral: Decimal
    pedagio: Decimal
    custo: Decimal
    subtotal: Decimal
    impostos: tuple[CalculatedTax, ...]
    total: Decimal

    @property
    def total_impostos(self) -> Decimal:
        return sum(
            (
                imposto.valor
                for imposto in self.impostos
            ),
            Decimal("0")
        )