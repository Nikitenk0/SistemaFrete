import unittest

from domain.models.driver_transport_provider_affiliation import (
    DriverTransportProviderRole,
)
from domain.models.transport_provider import (
    TransportProviderStatus,
    TransportProviderType,
)
from domain.models.vehicle_transport_provider_affiliation import (
    VehicleTransportProviderRelation,
)
from presentation.desktop.transport_provider_catalog_formatting import (
    driver_role_label,
    format_cpf,
    format_tax_document,
    provider_status_label,
    provider_type_label,
    vehicle_relation_label,
)


class TransportProviderCatalogFormattingTests(
    unittest.TestCase
):

    def test_formats_cnpj(self):
        self.assertEqual(
            format_tax_document(
                "12345678000190"
            ),
            "12.345.678/0001-90",
        )

    def test_formats_cpf(self):
        self.assertEqual(
            format_cpf(
                "12345678901"
            ),
            "123.456.789-01",
        )

    def test_labels(self):
        self.assertEqual(
            provider_type_label(
                TransportProviderType.COMPANY
            ),
            "Empresa",
        )
        self.assertEqual(
            provider_status_label(
                TransportProviderStatus.ACTIVE
            ),
            "Ativo",
        )
        self.assertEqual(
            driver_role_label(
                DriverTransportProviderRole.OWNER
            ),
            "Proprietário / sócio",
        )
        self.assertEqual(
            vehicle_relation_label(
                VehicleTransportProviderRelation.OWNED
            ),
            "Próprio",
        )


if __name__ == "__main__":
    unittest.main()
