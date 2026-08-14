from dataclasses import dataclass


@dataclass(frozen=True)
class RouteResult:
    origem: str
    destino: str
    distancia: str
    pedagio: str
    geral: str