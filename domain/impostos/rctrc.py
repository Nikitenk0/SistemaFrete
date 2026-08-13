from config.estados import ESTADOS
from config.impostos.matriz_rctrc import MATRIZ_RCTRC


_ESTADOS_NORMALIZADOS = {
    nome.casefold(): codigo
    for nome, codigo in ESTADOS.items()
}


def normalizar_estado(estado: str) -> str:

    if not isinstance(estado, str):
        raise ValueError(
            f"Estado inválido: {estado}"
        )

    estado_normalizado = estado.strip().casefold()

    if not estado_normalizado:
        raise ValueError(
            "Estado não pode estar vazio"
        )

    return estado_normalizado


def extrair_estado(localizacao: str) -> str:

    if not isinstance(localizacao, str):
        raise ValueError(
            f"Localização inválida: {localizacao}"
        )

    partes = localizacao.rsplit(
        "/",
        maxsplit=1
    )

    if len(partes) != 2:
        raise ValueError(
            f"Formato de localização inválido: {localizacao}"
        )

    estado = partes[1].strip()

    if not estado:
        raise ValueError(
            f"Não foi possível identificar o estado: {localizacao}"
        )

    return estado


def obter_codigo_estado(estado: str) -> int:

    estado_normalizado = normalizar_estado(
        estado
    )

    try:
        return _ESTADOS_NORMALIZADOS[
            estado_normalizado
        ]

    except KeyError as erro:
        raise ValueError(
            f"Estado não encontrado: {estado}"
        ) from erro


def obter_aliquota_rctrc(
    localizacao_origem: str,
    localizacao_destino: str
) -> float:

    estado_origem = extrair_estado(
        localizacao_origem
    )

    estado_destino = extrair_estado(
        localizacao_destino
    )

    codigo_origem = obter_codigo_estado(
        estado_origem
    )

    codigo_destino = obter_codigo_estado(
        estado_destino
    )

    # ESTADOS utiliza códigos de 1 a 27.
    # A matriz Python utiliza índices de 0 a 26.
    indice_origem = codigo_origem - 1
    indice_destino = codigo_destino - 1

    aliquota = MATRIZ_RCTRC[
        indice_origem
    ][
        indice_destino
    ]

    return float(
        aliquota
    )