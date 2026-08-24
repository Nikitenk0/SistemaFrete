import unittest
from decimal import Decimal
from unittest.mock import patch

from application.dtos.route_result import (
    RouteResult
)
from application.use_cases.calculate_quote_version import (
    CalculateQuoteVersion
)
from domain.models.customer import (
    CustomerPersonType
)
from domain.models.quote_transport_composition import (
    QuoteTransportComposition
)
from domain.models.quote_version import (
    QuoteVersion
)
from domain.pricing.default_policy import (
    DEFAULT_QUOTE_PRICING_POLICY
)


class FakeRouteSearcher:

    def __init__(
        self
    ) -> None:
        self.calls: list[
            tuple[str, str, int, bool]
        ] = []

    def search(
        self,
        origin: str,
        destination: str,
        axle_count: int,
        include_return_trip: bool
    ) -> RouteResult:

        self.calls.append(
            (
                origin,
                destination,
                axle_count,
                include_return_trip
            )
        )

        if axle_count == 6:
            return RouteResult(
                origem="São Paulo/São Paulo",
                destino="Campinas/São Paulo",
                distancia="500 km",
                pedagio="300,00",
                geral="1.500,00"
            )

        return RouteResult(
            origem="São Paulo/São Paulo",
            destino="Campinas/São Paulo",
            distancia="500 km",
            pedagio="220,00",
            geral="1.200,00"
        )


class FakePricingPolicyProvider:

    def get_effective_policy(
        self,
        _at
    ):
        return DEFAULT_QUOTE_PRICING_POLICY


class TestCalculateQuoteVersion(unittest.TestCase):

    @patch(
        "domain.pricing.insurance."
        "get_rctrc_rate",
        return_value=Decimal("0.04")
    )
    def test_searches_each_transport_composition(
        self,
        _rctrc_rate_mock
    ):

        route_searcher = FakeRouteSearcher()

        version = QuoteVersion(
            version_number=1,
            customer_person_type_snapshot=(
                CustomerPersonType.COMPANY
            ),
            customer_document_snapshot=(
                "12345678000195"
            ),
            customer_legal_name_snapshot=(
                "Cliente Teste Ltda."
            ),
            origin="São Paulo/São Paulo",
            destination="Campinas/São Paulo",
            invoice_value=Decimal("100000"),
            transport_compositions=(
                QuoteTransportComposition(
                    position=1,
                    axle_count=6
                ),
                QuoteTransportComposition(
                    position=2,
                    axle_count=4,
                    include_return_trip=True
                )
            )
        )

        result = CalculateQuoteVersion(
            route_searcher=route_searcher,
            pricing_policy_provider=(
                FakePricingPolicyProvider()
            )
        ).execute(
            version
        )

        self.assertEqual(
            route_searcher.calls,
            [
                (
                    "São Paulo/São Paulo",
                    "Campinas/São Paulo",
                    6,
                    False
                ),
                (
                    "São Paulo/São Paulo",
                    "Campinas/São Paulo",
                    4,
                    True
                )
            ]
        )

        self.assertEqual(
            result.driver_amount,
            Decimal("2700.00")
        )

        self.assertEqual(
            result.toll_amount,
            Decimal("520.00")
        )

        self.assertEqual(
            len(result.transport_compositions),
            2
        )

        self.assertEqual(
            result.transport_compositions[0].distance_km,
            Decimal("500")
        )

        self.assertEqual(
            result.transport_compositions[1].distance_km,
            Decimal("500")
        )

        self.assertEqual(
            result.insurance_components[2].value,
            Decimal("3.00")
        )

        self.assertEqual(
            result.insurance_components[3].value,
            Decimal("17.00")
        )


if __name__ == "__main__":
    unittest.main()
