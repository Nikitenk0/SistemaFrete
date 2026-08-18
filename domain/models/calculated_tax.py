from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class CalculatedTax:
    nome: str
    aliquota: Decimal
    base_calculo: Decimal
    valor: Decimal