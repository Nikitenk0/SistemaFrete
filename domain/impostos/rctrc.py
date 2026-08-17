from config.estados import ESTADOS
from config.impostos.matriz_rctrc import MATRIZ_RCTRC


_NORMALIZED_STATES = {
    state_name.casefold(): state_code
    for state_name, state_code in ESTADOS.items()
}


def normalize_state(estado: str) -> str:

    if not isinstance(estado, str):
        raise ValueError(
            f"Estado inválido: {estado}"
        )

    normalized_state = estado.strip().casefold()

    if not normalized_state:
        raise ValueError(
            "Estado não pode estar vazio"
        )

    return normalized_state


def extract_state(localizacao: str) -> str:

    if not isinstance(localizacao, str):
        raise ValueError(
            f"Localização inválida: {localizacao}"
        )

    parts = localizacao.rsplit(
        "/",
        maxsplit=1
    )

    if len(parts) != 2:
        raise ValueError(
            f"Formato de localização inválido: {localizacao}"
        )

    estado = parts[1].strip()

    if not estado:
        raise ValueError(
            f"Não foi possível identificar o estado: {localizacao}"
        )

    return estado


def get_state_code(estado: str) -> int:

    normalized_state = normalize_state(
        estado
    )

    try:
        return _NORMALIZED_STATES[
            normalized_state
        ]

    except KeyError as error:
        raise ValueError(
            f"Estado não encontrado: {estado}"
        ) from error


def get_rctrc_rate(
    localizacao_origem: str,
    localizacao_destino: str
) -> float:

    origin_state = extract_state(
        localizacao_origem
    )

    destination_state = extract_state(
        localizacao_destino
    )

    origin_state_code = get_state_code(
        origin_state
    )

    destination_state_code = get_state_code(
        destination_state
    )

    # ESTADOS utiliza códigos de 1 a 27.
    # A matriz Python utiliza índices de 0 a 26.
    origin_matrix_index = origin_state_code - 1
    destination_matrix_index = destination_state_code - 1

    aliquota = MATRIZ_RCTRC[
        origin_matrix_index
    ][
        destination_matrix_index
    ]

    return float(
        aliquota
    )