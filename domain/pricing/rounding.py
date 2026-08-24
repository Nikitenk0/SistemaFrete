from decimal import (
    Decimal,
    ROUND_HALF_UP
)


PRICE_ROUNDING_STEP = Decimal(
    "50"
)


def round_price(
    value: Decimal
) -> Decimal:

    if value < 0:
        raise ValueError(
            "Preço não pode ser negativo"
        )

    step_count = (
        value
        / PRICE_ROUNDING_STEP
    ).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP
    )

    return (
        step_count
        * PRICE_ROUNDING_STEP
    )