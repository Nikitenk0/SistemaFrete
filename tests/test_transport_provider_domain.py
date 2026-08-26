import unittest
from datetime import (
    datetime,
    timedelta,
    timezone,
)

from domain.models.driver_transport_provider_affiliation import (
    DriverTransportProviderAffiliation,
    DriverTransportProviderRole,
)
from domain.models.transport_provider import (
    TransportProvider,
    TransportProviderStatus,
    TransportProviderType,
)
from domain.models.vehicle_transport_provider_affiliation import (
    VehicleTransportProviderAffiliation,
    VehicleTransportProviderRelation,
)


NOW = datetime(
    2026,
    8,
    26,
    12,
    0,
    tzinfo=timezone.utc,
)


class TransportProviderDomainTests(
    unittest.TestCase
):

    def test_company_provider_supports_owner_driver_scenario(self):
        provider = TransportProvider(
            legal_name="Exemplo 123 Transportes LTDA",
            trade_name="Exemplo 123",
            tax_document="12.345.678/0001-90",
            provider_type=TransportProviderType.COMPANY,
        )

        self.assertEqual(
            provider.tax_document,
            "12345678000190",
        )
        self.assertEqual(
            provider.status,
            TransportProviderStatus.ACTIVE,
        )

    def test_individual_provider_requires_cpf_length(self):
        provider = TransportProvider(
            legal_name="João Transportador",
            tax_document="123.456.789-01",
            provider_type=TransportProviderType.INDIVIDUAL,
        )

        self.assertEqual(
            provider.tax_document,
            "12345678901",
        )

    def test_rejects_document_incompatible_with_provider_type(self):
        with self.assertRaisesRegex(
            ValueError,
            "incompatível",
        ):
            TransportProvider(
                legal_name="Empresa",
                tax_document="12345678901",
                provider_type=TransportProviderType.COMPANY,
            )

    def test_driver_can_be_owner_of_company(self):
        affiliation = DriverTransportProviderAffiliation(
            driver_id=10,
            transport_provider_id=20,
            role=DriverTransportProviderRole.OWNER,
            started_at=NOW,
        )

        self.assertTrue(
            affiliation.is_active
        )
        self.assertEqual(
            affiliation.role,
            DriverTransportProviderRole.OWNER,
        )

    def test_vehicle_can_be_owned_by_same_company(self):
        affiliation = VehicleTransportProviderAffiliation(
            vehicle_id=30,
            transport_provider_id=20,
            relation=VehicleTransportProviderRelation.OWNED,
            started_at=NOW,
        )

        self.assertTrue(
            affiliation.is_active
        )
        self.assertEqual(
            affiliation.transport_provider_id,
            20,
        )

    def test_closed_driver_affiliation_is_not_active(self):
        affiliation = DriverTransportProviderAffiliation(
            driver_id=10,
            transport_provider_id=20,
            role=DriverTransportProviderRole.EMPLOYEE,
            started_at=NOW,
            ended_at=NOW + timedelta(days=30),
        )

        self.assertFalse(
            affiliation.is_active
        )

    def test_rejects_affiliation_end_before_start(self):
        with self.assertRaisesRegex(
            ValueError,
            "anterior",
        ):
            VehicleTransportProviderAffiliation(
                vehicle_id=30,
                transport_provider_id=20,
                relation=VehicleTransportProviderRelation.OWNED,
                started_at=NOW,
                ended_at=NOW - timedelta(seconds=1),
            )


if __name__ == "__main__":
    unittest.main()
