from decimal import (
    Decimal,
    InvalidOperation
)


def parse_distance_km(
    value: str | int | float | Decimal
) -> Decimal:

    if isinstance(value, bool):
        raise ValueError(
            "Distância inválida"
        )

    if isinstance(value, Decimal):
        distance = value

    elif isinstance(value, (int, float)):
        distance = Decimal(
            str(value)
        )

    elif isinstance(value, str):

        text = value.strip().casefold()

        text = text.replace(
            "km",
            ""
        )

        text = "".join(
            text.split()
        )

        if not text:
            raise ValueError(
                "Distância vazia"
            )

        if "," in text:

            text = text.replace(
                ".",
                ""
            )

            text = text.replace(
                ",",
                "."
            )

        try:

            distance = Decimal(
                text
            )

        except InvalidOperation as error:

            raise ValueError(
                "Distância inválida"
            ) from error

    else:
        raise ValueError(
            "Distância inválida"
        )

    if distance < 0:
        raise ValueError(
            "Distância não pode ser negativa"
        )

    return distance