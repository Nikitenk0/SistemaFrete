from dataclasses import dataclass


@dataclass(frozen=True)
class ImpostoCalculado:
    nome: str
    aliquota: float
    base_calculo: float
    valor: float