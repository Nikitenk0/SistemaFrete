def converter_valor_monetario(
    valor: str | int | float
) -> float:

    if isinstance(valor, bool):
        raise ValueError(
            f"Valor monetário inválido: {valor}"
        )

    if isinstance(valor, (int, float)):
        return float(valor)

    if not isinstance(valor, str):
        raise ValueError(
            f"Valor monetário inválido: {valor}"
        )

    texto = valor.strip()

    texto = texto.replace(
        "R$",
        ""
    )

    # Remove espaços, inclusive espaços especiais.
    texto = "".join(
        texto.split()
    )

    if not texto:
        raise ValueError(
            "Valor monetário vazio"
        )

    # ==========================================================
    # FORMATO BRASILEIRO
    #
    # 6.143,83
    # 150.000,50
    # 6143,83
    # ==========================================================

    if "," in texto:

        texto = texto.replace(
            ".",
            ""
        )

        texto = texto.replace(
            ",",
            "."
        )

    # ==========================================================
    # SEM VÍRGULA
    #
    # 6143.83       -> decimal
    # 150000.50     -> decimal
    # 150.000       -> milhar
    # 1.234.567     -> milhar
    # ==========================================================

    else:

        quantidade_pontos = texto.count(
            "."
        )

        if quantidade_pontos > 1:

            texto = texto.replace(
                ".",
                ""
            )

        elif quantidade_pontos == 1:

            parte_inteira, parte_decimal = texto.split(
                ".",
                maxsplit=1
            )

            parte_inteira_sem_sinal = (
                parte_inteira.lstrip("+-")
            )

            # Em valores monetários, três dígitos
            # após o ponto são tratados como milhar.
            #
            # 150.000 -> 150000
            if (
                parte_inteira_sem_sinal.isdigit()
                and parte_decimal.isdigit()
                and len(parte_decimal) == 3
            ):

                texto = (
                    parte_inteira
                    + parte_decimal
                )

    try:

        return float(
            texto
        )

    except ValueError as erro:

        raise ValueError(
            f"Não foi possível converter o valor: {valor}"
        ) from erro