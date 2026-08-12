from config.custos import obter_custo
from config.estados import ESTADOS
from config.impostos.matriz_rctrc import MATRIZ_IMPOSTO


# ==========================================================
# CONVERSÃO DE VALORES
# ==========================================================

def converter_valor(valor):
    """
    Converte valores numéricos ou valores formatados
    como moeda brasileira para float.

    Exemplos:
        6143.83
        "6143.83"
        "R$ 6.143,83"
        "6.143,83"
    """

    if isinstance(valor, (int, float)):
        return float(valor)

    if not isinstance(valor, str):
        raise ValueError(
            f"Valor inválido: {valor}"
        )

    valor = valor.strip()

    # Remove R$
    valor = valor.replace("R$", "").strip()

    # Remove separador de milhar
    valor = valor.replace(".", "")

    # Converte vírgula decimal para ponto
    valor = valor.replace(",", ".")

    try:
        return float(valor)

    except ValueError:
        raise ValueError(
            f"Não foi possível converter o valor: {valor}"
        )


# ==========================================================
# NORMALIZAÇÃO DO ESTADO
# ==========================================================

def normalizar_estado(estado):
    """
    Normaliza o nome do estado para facilitar
    a busca no dicionário ESTADOS.
    """

    if not isinstance(estado, str):
        raise ValueError(
            f"Estado inválido: {estado}"
        )

    return estado.strip().lower()

# ==========================================================
# EXTRAIR ESTADO DA LOCALIZAÇÃO
# ==========================================================

def extrair_estado(localizacao):
    """
    Recebe uma localização no formato:

        "Porto Alegre / Rio Grande do Sul"

    e retorna somente o nome do estado:

        "Rio Grande do Sul"
    """

    if not isinstance(localizacao, str):
        raise ValueError(
            f"Localização inválida: {localizacao}"
        )

    if "/" not in localizacao:
        raise ValueError(
            f"Formato de localização inválido: {localizacao}"
        )

    estado = localizacao.split("/")[-1].strip()

    if not estado:
        raise ValueError(
            f"Não foi possível identificar o estado: {localizacao}"
        )

    return estado


# ==========================================================
# OBTER NÚMERO DO ESTADO
# ==========================================================

def obter_numero_estado(estado):
    """
    Recebe o nome do estado e retorna seu número
    correspondente na matriz.
    """

    estado_normalizado = normalizar_estado(estado)

    for nome_estado, numero in ESTADOS.items():

        if normalizar_estado(nome_estado) == estado_normalizado:
            return numero

    raise ValueError(
        f"Estado não encontrado na tabela de estados: {estado}"
    )


# ==========================================================
# OBTER PERCENTUAL DO IMPOSTO
# ==========================================================

def obter_percentual_imposto(
    localizacao_origem,
    localizacao_destino
):
    """
    Localiza na matriz 27x27 o percentual de imposto
    correspondente à combinação:

        Localização Origem x Localização Destino

    Exemplo:

        "Porto Alegre / Rio Grande do Sul"
        "Curitiba / Paraná"

    Internamente:

        Rio Grande do Sul -> número do estado
        Paraná             -> número do estado
    """

    # ======================================================
    # EXTRAI SOMENTE OS ESTADOS
    # ======================================================

    estado_origem = extrair_estado(
        localizacao_origem
    )

    estado_destino = extrair_estado(
        localizacao_destino
    )

    # ======================================================
    # OBTÉM OS NÚMEROS DOS ESTADOS
    # ======================================================

    numero_origem = obter_numero_estado(
        estado_origem
    )

    numero_destino = obter_numero_estado(
        estado_destino
    )

    # ======================================================
    # ACESSA A MATRIZ
    # ======================================================

    percentual = MATRIZ_IMPOSTO[
        numero_origem - 1
    ][
        numero_destino - 1
    ]

    return float(percentual)


# ==========================================================
# CALCULAR ORÇAMENTO
# ==========================================================

def calcular_orcamento(
    valor_nota,
    geral,
    pedagio,
    estado_origem,
    estado_destino
):
    """
    Calcula o orçamento completo.

    Fórmula:

        Custo:
            Valor de nota <= 200.000
                R$ 350,00

            Valor de nota > 200.000
                R$ 550,00

        Base do imposto:
            Geral + Pedágio + Custo

        Imposto:
            Base do imposto × percentual

        Total:
            Base do imposto + Imposto
    """

    # ======================================================
    # CONVERTE VALORES
    # ======================================================

    valor_nota = converter_valor(
        valor_nota
    )

    geral = converter_valor(
        geral
    )

    pedagio = converter_valor(
        pedagio
    )

    # ======================================================
    # OBTÉM CUSTO
    # ======================================================

    custo = obter_custo(
        valor_nota
    )

    # ======================================================
    # OBTÉM PERCENTUAL DO IMPOSTO
    # ======================================================

    percentual_imposto = obter_percentual_imposto(
        estado_origem,
        estado_destino
    )

    # ======================================================
    # BASE DO IMPOSTO
    # ======================================================

    base_imposto = (
        geral
        + pedagio
        + custo
    )

    # ======================================================
    # VALOR DO IMPOSTO
    # ======================================================

    valor_imposto = (
        base_imposto
        * percentual_imposto
    )

    # ======================================================
    # TOTAL
    # ======================================================

    total = (
        base_imposto
        + valor_imposto
    )

    # ======================================================
    # RETORNO
    # ======================================================

    return {
        "valor_nota": valor_nota,
        "geral": geral,
        "pedagio": pedagio,
        "custo": custo,
        "estado_origem": estado_origem,
        "estado_destino": estado_destino,
        "percentual_imposto": percentual_imposto,
        "base_imposto": base_imposto,
        "valor_imposto": valor_imposto,
        "total": total
    }