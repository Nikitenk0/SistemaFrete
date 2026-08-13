from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoRota:
    origem: str
    destino: str
    distancia: str
    pedagio: str
    geral: str