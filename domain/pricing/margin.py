from decimal import Decimal

from domain.models.quote_pricing_policy import (
    MarginBand,
    QuotePricingPolicy
)


def calculate_margin(
    bp02: Decimal,
    pricing_policy: QuotePricingPolicy
) -> tuple[
    MarginBand,
    Decimal
]:

    if bp02 < 0:
        raise ValueError(
            "BP02 não pode ser negativo"
        )

    margin_band = (
        pricing_policy.margin_band_for(
            bp02
        )
    )

    margin_value = (
        bp02
        * margin_band.rate
    )

    return (
        margin_band,
        margin_value
    )