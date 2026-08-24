from dataclasses import dataclass
from decimal import Decimal

from domain.models.quote_insurance_component import (
    QuoteInsuranceComponent
)


@dataclass(frozen=True)
class QuotePricingResult:

    invoice_value: Decimal

    driver_amount: Decimal
    toll_amount: Decimal

    additional_total: Decimal

    insurance_components: tuple[
        QuoteInsuranceComponent,
        ...
    ]

    freight_insurance_total: Decimal

    bp01: Decimal

    tracking_required: bool

    administrative_rate: Decimal
    administrative_minimum: Decimal
    administrative_cost: Decimal

    bp02: Decimal

    margin_band_minimum: Decimal | None
    margin_band_maximum: Decimal | None

    standard_margin_rate: Decimal
    standard_margin_value: Decimal

    target_net_value: Decimal

    tax_rate: Decimal
    tax_value: Decimal

    calculated_price: Decimal
    rounded_price: Decimal