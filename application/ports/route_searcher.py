from typing import Protocol

from application.dtos.route_result import RouteResult


class RouteSearcher(Protocol):

    def search(
        self,
        origem: str,
        destino: str,
        quantidade_eixos: int,
        calcular_volta: bool
    ) -> RouteResult | None:
        ...