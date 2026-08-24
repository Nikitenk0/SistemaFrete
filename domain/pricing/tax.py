from decimal import Decimal


def calculate_gross_price(
    target_net_value: Decimal,
    tax_rate: Decimal
) -> tuple[
    Decimal,
    Decimal
]:

    if target_net_value < 0:
        raise ValueError(
            "Valor líquido alvo não pode "
            "ser negativo"
        )

    if (
        tax_rate < 0
        or tax_rate >= 1
    ):
        raise ValueError(
            "Taxa de imposto inválida"
        )

    gross_price = (
        target_net_value
        / (
            Decimal("1")
            - tax_rate
        )
    )

    tax_value = (
        gross_price
        * tax_rate
    )

    return (
        gross_price,
        tax_value
    )