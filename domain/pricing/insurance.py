from decimal import Decimal

from domain.impostos.rctrc import (
    get_rctrc_rate
)
from domain.models.quote_insurance_component import (
    QuoteInsuranceComponent,
    QuoteInsuranceType
)


PERCENT_DIVISOR = Decimal(
    "100"
)

RCDC_RATE = Decimal(
    "0.00022"
)

LIFE_INSURANCE_VALUE = Decimal(
    "1.50"
)

ACCIDENT_INSURANCE_VALUE = Decimal(
    "8.50"
)


def calculate_insurance_components(
    invoice_value: Decimal,
    origin: str,
    destination: str,
    vehicle_count: int
) -> tuple[
    QuoteInsuranceComponent,
    ...
]:

    if invoice_value < 0:
        raise ValueError(
            "Valor da nota não pode "
            "ser negativo"
        )

    if vehicle_count < 1:
        raise ValueError(
            "Quantidade de veículos inválida"
        )

    rctrc_percentage = get_rctrc_rate(
        origin,
        destination
    )

    rctrc_rate = (
        rctrc_percentage
        / PERCENT_DIVISOR
    )

    rctrc_value = (
        invoice_value
        * rctrc_rate
    )

    rcdc_value = (
        invoice_value
        * RCDC_RATE
    )

    vehicle_count_decimal = Decimal(
        vehicle_count
    )

    life_value = (
        vehicle_count_decimal
        * LIFE_INSURANCE_VALUE
    )

    accident_value = (
        vehicle_count_decimal
        * ACCIDENT_INSURANCE_VALUE
    )

    return (
        QuoteInsuranceComponent(
            insurance_type=(
                QuoteInsuranceType.RCTRC
            ),
            calculation_base=invoice_value,
            rate=rctrc_rate,
            value=rctrc_value,
            position=1
        ),
        QuoteInsuranceComponent(
            insurance_type=(
                QuoteInsuranceType.RCDC
            ),
            calculation_base=invoice_value,
            rate=RCDC_RATE,
            value=rcdc_value,
            position=2
        ),
        QuoteInsuranceComponent(
            insurance_type=(
                QuoteInsuranceType.LIFE
            ),
            calculation_base=(
                vehicle_count_decimal
            ),
            rate=LIFE_INSURANCE_VALUE,
            value=life_value,
            position=3
        ),
        QuoteInsuranceComponent(
            insurance_type=(
                QuoteInsuranceType.ACCIDENT
            ),
            calculation_base=(
                vehicle_count_decimal
            ),
            rate=(
                ACCIDENT_INSURANCE_VALUE
            ),
            value=accident_value,
            position=4
        ),
    )
