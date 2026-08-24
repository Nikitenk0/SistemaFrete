import unittest
from decimal import Decimal
from unittest.mock import patch

from domain.models.quote_transport_composition import (
    QuoteTransportComposition
)
from domain.pricing.default_policy import (
    DEFAULT_QUOTE_PRICING_POLICY
)
from domain.pricing.quote_pricing import (
    calculate_quote_pricing
)
from domain.pricing.rounding import (
    round_price
)


class TestQuotePricing(unittest.TestCase):

    @patch(
        "domain.pricing.insurance."
        "get_rctrc_rate",
        return_value=Decimal("0.04")
    )
    def test_calculates_complete_quote_pricing(
        self,
        rctrc_rate_mock
    ):

        composition = QuoteTransportComposition(
            position=1,
            axle_count=6,
            distance_km=Decimal("100"),
            driver_amount=Decimal("1000"),
            toll_amount=Decimal("100")
        )

        result = calculate_quote_pricing(
            invoice_value=Decimal("100000"),
            transport_compositions=(
                composition,
            ),
            origin="São Paulo/São Paulo",
            destination="Campinas/São Paulo",
            tracking_required=False,
            pricing_policy=(
                DEFAULT_QUOTE_PRICING_POLICY
            )
        )

        rctrc_rate_mock.assert_called_once_with(
            "São Paulo/São Paulo",
            "Campinas/São Paulo"
        )

        rctrc = result.insurance_components[0]
        rcdc = result.insurance_components[1]
        life = result.insurance_components[2]
        accident = result.insurance_components[3]

        self.assertEqual(
            rctrc.calculation_base,
            Decimal("100000")
        )

        self.assertEqual(
            rctrc.rate,
            Decimal("0.0004")
        )

        self.assertEqual(
            rctrc.value,
            Decimal("40")
        )

        self.assertEqual(
            rcdc.value,
            Decimal("22")
        )

        self.assertEqual(
            life.calculation_base,
            Decimal("1")
        )

        self.assertEqual(
            life.value,
            Decimal("1.50")
        )

        self.assertEqual(
            accident.value,
            Decimal("8.50")
        )

        self.assertEqual(
            result.freight_insurance_total,
            Decimal("72.00")
        )

        self.assertEqual(
            result.driver_amount,
            Decimal("1000")
        )

        self.assertEqual(
            result.toll_amount,
            Decimal("100")
        )

        self.assertEqual(
            result.bp01,
            Decimal("1172.00")
        )

        self.assertEqual(
            result.administrative_rate,
            Decimal("0.04")
        )

        self.assertEqual(
            result.administrative_cost,
            Decimal("200")
        )

        self.assertEqual(
            result.bp02,
            Decimal("1372.00")
        )

        self.assertEqual(
            result.standard_margin_rate,
            Decimal("0.22")
        )

        self.assertEqual(
            result.standard_margin_value,
            Decimal("301.8400")
        )

        self.assertEqual(
            result.target_net_value,
            Decimal("1673.8400")
        )

        self.assertEqual(
            result.tax_rate,
            Decimal("0.20")
        )

        self.assertEqual(
            result.calculated_price,
            Decimal("2092.300")
        )

        self.assertEqual(
            result.tax_value,
            Decimal("418.46000")
        )

        self.assertEqual(
            result.rounded_price,
            Decimal("2100")
        )

    @patch(
        "domain.pricing.insurance."
        "get_rctrc_rate",
        return_value=Decimal("0.04")
    )
    def test_aggregates_multiple_transport_compositions(
        self,
        _rctrc_rate_mock
    ):

        compositions = (
            QuoteTransportComposition(
                position=1,
                axle_count=6,
                distance_km=Decimal("500"),
                driver_amount=Decimal("1500"),
                toll_amount=Decimal("300")
            ),
            QuoteTransportComposition(
                position=2,
                axle_count=4,
                distance_km=Decimal("500"),
                driver_amount=Decimal("1200"),
                toll_amount=Decimal("220")
            )
        )

        result = calculate_quote_pricing(
            invoice_value=Decimal("100000"),
            transport_compositions=(
                compositions
            ),
            origin="São Paulo/São Paulo",
            destination="Campinas/São Paulo",
            tracking_required=False,
            pricing_policy=(
                DEFAULT_QUOTE_PRICING_POLICY
            )
        )

        self.assertEqual(
            result.driver_amount,
            Decimal("2700")
        )

        self.assertEqual(
            result.toll_amount,
            Decimal("520")
        )

        self.assertEqual(
            result.insurance_components[2].value,
            Decimal("3.00")
        )

        self.assertEqual(
            result.insurance_components[3].value,
            Decimal("17.00")
        )

        self.assertEqual(
            result.freight_insurance_total,
            Decimal("82.00")
        )

        self.assertEqual(
            result.bp01,
            Decimal("3302.00")
        )

        self.assertEqual(
            result.bp02,
            Decimal("3502.00")
        )

        self.assertEqual(
            result.standard_margin_rate,
            Decimal("0.18")
        )

    def test_uses_tracking_policy(
        self
    ):

        policy = (
            DEFAULT_QUOTE_PRICING_POLICY
            .administrative_policy_for(
                True
            )
        )

        self.assertEqual(
            policy.rate,
            Decimal("0.07")
        )

        self.assertEqual(
            policy.minimum_value,
            Decimal("200")
        )

    def test_uses_15_6_percent_band(
        self
    ):

        band = (
            DEFAULT_QUOTE_PRICING_POLICY
            .margin_band_for(
                Decimal("23000")
            )
        )

        self.assertEqual(
            band.rate,
            Decimal("0.156")
        )

    def test_rounds_to_nearest_50(
        self
    ):

        self.assertEqual(
            round_price(
                Decimal("1024.99")
            ),
            Decimal("1000")
        )

        self.assertEqual(
            round_price(
                Decimal("1025")
            ),
            Decimal("1050")
        )


if __name__ == "__main__":
    unittest.main()
