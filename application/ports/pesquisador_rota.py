from typing import Protocol

from domain.models.resultado_rota import ResultadoRota


class PesquisadorRota(Protocol):

    def pesquisar(
        self,
        origem: str,
        destino: str,
        quantidade_eixos: int,
        calcular_volta: bool
    ) -> ResultadoRota | None:
        ...