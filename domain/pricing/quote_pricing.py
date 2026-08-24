from decimal import Decimal

from domain.models.quote_additional import (
    QuoteAdditional
)
from domain.models.quote_pricing_policy import (
    QuotePricingPolicy
)
from domain.models.quote_pricing_result import (
    QuotePricingResult
)
from domain.models.quote_transport_composition import (
    QuoteTransportComposition
)
from domain.pricing.administrative_cost import (
    calculate_administrative_cost
)
from domain.pricing.insurance import (
    calculate_insurance_components
)
from domain.pricing.margin import (
    calculate_margin
)
from domain.pricing.rounding import (
    round_price
)
from domain.pricing.tax import (
    calculate_gross_price
)


def calculate_quote_pricing(
    invoice_value: Decimal,
    transport_compositions: tuple[
        QuoteTransportComposition,
        ...
    ],
    origin: str,
    destination: str,
    tracking_required: bool,
    pricing_policy: QuotePricingPolicy,
    additionals: tuple[
        QuoteAdditional,
        ...
    ] = ()
) -> QuotePricingResult:

    if invoice_value < 0:
        raise ValueError(
            "Valor da nota não pode ser negativo"
        )

    if not origin.strip():
        raise ValueError(
            "Origem é obrigatória"
        )

    if not destination.strip():
        raise ValueError(
            "Destino é obrigatório"
        )

    if not transport_compositions:
        raise ValueError(
            "Orçamento precisa possuir "
            "ao menos uma composição de transporte"
        )

    for composition in transport_compositions:

        if composition.driver_amount is None:
            raise ValueError(
                "Valor Motorista não calculado "
                f"na composição {composition.position}"
            )

        if composition.toll_amount is None:
            raise ValueError(
                "Pedágio não calculado "
                f"na composição {composition.position}"
            )

    driver_amount = sum(
        (
            composition.driver_amount
            for composition
            in transport_compositions
            if composition.driver_amount
            is not None
        ),
        Decimal("0")
    )

    toll_amount = sum(
        (
            composition.toll_amount
            for composition
            in transport_compositions
            if composition.toll_amount
            is not None
        ),
        Decimal("0")
    )

    additional_total = sum(
        (
            additional.value
            for additional
            in additionals
        ),
        Decimal("0")
    )

    insurance_components = (
        calculate_insurance_components(
            invoice_value=invoice_value,
            origin=origin,
            destination=destination,
            vehicle_count=len(
                transport_compositions
            )
        )
    )

    freight_insurance_total = sum(
        (
            component.value
            for component
            in insurance_components
        ),
        Decimal("0")
    )

    bp01 = (
        driver_amount
        + toll_amount
        + additional_total
        + freight_insurance_total
    )

    administrative_policy = (
        pricing_policy
        .administrative_policy_for(
            tracking_required
        )
    )

    administrative_cost = (
        calculate_administrative_cost(
            bp01=bp01,
            policy=administrative_policy
        )
    )

    bp02 = (
        bp01
        + administrative_cost
    )

    (
        margin_band,
        standard_margin_value
    ) = calculate_margin(
        bp02=bp02,
        pricing_policy=pricing_policy
    )

    target_net_value = (
        bp02
        + standard_margin_value
    )

    (
        calculated_price,
        tax_value
    ) = calculate_gross_price(
        target_net_value=(
            target_net_value
        ),
        tax_rate=(
            pricing_policy.tax_rate
        )
    )

    rounded_price = round_price(
        calculated_price
    )

    return QuotePricingResult(
        invoice_value=invoice_value,
        driver_amount=driver_amount,
        toll_amount=toll_amount,
        additional_total=additional_total,
        insurance_components=(
            insurance_components
        ),
        freight_insurance_total=(
            freight_insurance_total
        ),
        bp01=bp01,
        tracking_required=(
            tracking_required
        ),
        administrative_rate=(
            administrative_policy.rate
        ),
        administrative_minimum=(
            administrative_policy
            .minimum_value
        ),
        administrative_cost=(
            administrative_cost
        ),
        bp02=bp02,
        margin_band_minimum=(
            margin_band
            .lower_bound_exclusive
        ),
        margin_band_maximum=(
            margin_band
            .upper_bound_inclusive
        ),
        standard_margin_rate=(
            margin_band.rate
        ),
        standard_margin_value=(
            standard_margin_value
        ),
        target_net_value=(
            target_net_value
        ),
        tax_rate=(
            pricing_policy.tax_rate
        ),
        tax_value=tax_value,
        calculated_price=(
            calculated_price
        ),
        rounded_price=rounded_price
    )
