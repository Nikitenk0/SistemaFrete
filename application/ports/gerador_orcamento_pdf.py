from typing import Protocol

from domain.models.resultado_orcamento import ResultadoOrcamento
from domain.models.resultado_rota import ResultadoRota


class GeradorOrcamentoPdf(Protocol):

    def gerar(
        self,
        resultado_rota: ResultadoRota,
        resultado_orcamento: ResultadoOrcamento,
        quantidade_eixos: int,
        calcular_volta: bool,
        caminho: str
    ) -> None:
        ...
        