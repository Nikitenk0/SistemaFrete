from dataclasses import dataclass


@dataclass(frozen=True)
class CalculatedTax:
    nome: str
    aliquota: float
    base_calculo: float
    valor: float