from decimal import Decimal

from domain.models.quote_pricing_policy import (
    AdministrativeCostPolicy
)


def calculate_administrative_cost(
    bp01: Decimal,
    policy: AdministrativeCostPolicy
) -> Decimal:

    if bp01 < 0:
        raise ValueError(
            "BP01 não pode ser negativo"
        )

    percentage_value = (
        bp01
        * policy.rate
    )

    return max(
        policy.minimum_value,
        percentage_value
    )