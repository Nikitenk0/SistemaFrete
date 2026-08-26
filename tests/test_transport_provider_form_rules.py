import unittest

from domain.models.transport_provider import TransportProviderType
from presentation.desktop.transport_provider_form_rules import (
    get_transport_provider_form_presentation,
)


class TransportProviderFormRulesTests(unittest.TestCase):

    def test_individual_hides_trade_name(self):
        presentation = get_transport_provider_form_presentation(
            TransportProviderType.INDIVIDUAL
        )

        self.assertEqual(
            presentation.name_label,
            "Nome completo",
        )
        self.assertEqual(
            presentation.document_label,
            "CPF",
        )
        self.assertFalse(
            presentation.show_trade_name
        )

    def test_company_shows_trade_name(self):
        presentation = get_transport_provider_form_presentation(
            TransportProviderType.COMPANY
        )

        self.assertEqual(
            presentation.name_label,
            "Razão social",
        )
        self.assertEqual(
            presentation.document_label,
            "CNPJ",
        )
        self.assertTrue(
            presentation.show_trade_name
        )


if __name__ == "__main__":
    unittest.main()
