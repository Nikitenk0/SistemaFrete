from decimal import Decimal, InvalidOperation


def parse_monetary_value(
    valor: str | int | float | Decimal
) -> Decimal:

    if isinstance(valor, bool):
        raise ValueError(
            f"Valor monetário inválido: {valor}"
        )

    if isinstance(valor, Decimal):
        return valor

    if isinstance(valor, (int, float)):
        return Decimal(
            str(valor)
        )

    if not isinstance(valor, str):
        raise ValueError(
            f"Valor monetário inválido: {valor}"
        )

    text = valor.strip()

    text = text.replace(
        "R$",
        ""
    )

    # Remove espaços, inclusive espaços especiais.
    text = "".join(
        text.split()
    )

    if not text:
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

    if "," in text:

        text = text.replace(
            ".",
            ""
        )

        text = text.replace(
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

        dot_count = text.count(
            "."
        )

        if dot_count > 1:

            text = text.replace(
                ".",
                ""
            )

        elif dot_count == 1:

            integer_part, decimal_part = text.split(
                ".",
                maxsplit=1
            )

            unsigned_integer_part = (
                integer_part.lstrip("+-")
            )

            # Em valores monetários, três dígitos
            # após o ponto são tratados como milhar.
            #
            # 150.000 -> 150000
            if (
                unsigned_integer_part.isdigit()
                and decimal_part.isdigit()
                and len(decimal_part) == 3
            ):

                text = (
                    integer_part
                    + decimal_part
                )

    try:

        return Decimal(
            text
        )

    except InvalidOperation as error:

        raise ValueError(
            f"Não foi possível converter o valor: {valor}"
        ) from error