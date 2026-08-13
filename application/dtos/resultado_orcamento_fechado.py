from dataclasses import dataclass

from domain.models.resultado_orcamento import ResultadoOrcamento
from domain.models.resultado_rota import ResultadoRota


@dataclass(frozen=True)
class ResultadoOrcamentoFechado:
    rota: ResultadoRota
    orcamento: ResultadoOrcamento