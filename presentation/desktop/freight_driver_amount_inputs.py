from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_HALF_UP,
)


_CENT = Decimal("0.01")


def parse_actual_driver_amount(
    value_text: str,
) -> Decimal:
    if not isinstance(value_text, str):
        raise ValueError(
            "Valor realizado inválido"
        )

    normalized = (
        value_text
        .strip()
        .replace("R$", "")
        .replace(" ", "")
    )

    if not normalized:
        raise ValueError(
            "Informe o valor realizado do motorista"
        )

    if "," in normalized:
        normalized = (
            normalized
            .replace(".", "")
            .replace(",", ".")
        )

    try:
        value = Decimal(normalized)
    except InvalidOperation as error:
        raise ValueError(
            "Valor realizado inválido"
        ) from error

    if not value.is_finite() or value < Decimal("0"):
        raise ValueError(
            "Valor realizado inválido"
        )

    return value.quantize(
        _CENT,
        rounding=ROUND_HALF_UP,
    )
