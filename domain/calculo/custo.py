from domain.calculo.custos import (
    LIMITE_VALOR_NOTA,
    CUSTO_ATE_LIMITE,
    CUSTO_ACIMA_LIMITE,
)


def calcular_custo(
    valor_nota: float
) -> float:

    if valor_nota <= LIMITE_VALOR_NOTA:
        return CUSTO_ATE_LIMITE

    return CUSTO_ACIMA_LIMITE