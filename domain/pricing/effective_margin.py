from decimal import Decimal


def calculate_effective_margin(
    gross_price: Decimal,
    bp02: Decimal,
    tax_rate: Decimal
) -> tuple[
    Decimal,
    Decimal | None
]:

    if gross_price < 0:
        raise ValueError(
            "Preço bruto não pode ser negativo"
        )

    if bp02 < 0:
        raise ValueError(
            "BP02 não pode ser negativo"
        )

    if tax_rate < 0 or tax_rate >= 1:
        raise ValueError(
            "Taxa de imposto inválida"
        )

    net_after_tax = (
        gross_price
        * (
            Decimal("1")
            - tax_rate
        )
    )

    margin_value = (
        net_after_tax
        - bp02
    )

    margin_rate = (
        margin_value / bp02
        if bp02 != 0
        else None
    )

    return (
        margin_value,
        margin_rate
    )
