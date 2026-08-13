from dataclasses import dataclass

from domain.models.imposto_calculado import ImpostoCalculado


@dataclass(frozen=True)
class ResultadoOrcamento:
    valor_nota: float
    geral: float
    pedagio: float
    custo: float
    subtotal: float
    impostos: tuple[ImpostoCalculado, ...]
    total: float

    @property
    def total_impostos(self) -> float:
        return sum(
            imposto.valor
            for imposto in self.impostos
        )