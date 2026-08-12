LIMITE_VALOR_NOTA = 200_000

CUSTO_ATE_LIMITE = 350.00
CUSTO_ACIMA_LIMITE = 550.00


def obter_custo(valor_nota):
    """
    Retorna o custo fixo de acordo com o valor da nota.
    """

    if valor_nota <= LIMITE_VALOR_NOTA:
        return CUSTO_ATE_LIMITE

    return CUSTO_ACIMA_LIMITE