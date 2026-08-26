import unittest
from datetime import datetime, timezone
from decimal import Decimal

from domain.models.freight import FreightStatus
from domain.models.freight_event import FreightEventType
from domain.models.freight_expense import FreightExpenseType
from domain.models.freight_vehicle_record import FreightVehicleType
from presentation.desktop.freight_detail_formatting import (
    event_label,
    expense_label,
    format_currency,
    format_datetime,
    format_margin,
    optional_text,
    status_label,
    vehicle_label,
    yes_no,
)


class FreightDetailFormattingTests(unittest.TestCase):

    def test_formats_currency_in_brazilian_notation(self):
        self.assertEqual(
            format_currency(Decimal("12345.67")),
            "R$ 12.345,67",
        )

    def test_formats_none_currency(self):
        self.assertEqual(format_currency(None), "--")

    def test_formats_margin_as_percentage(self):
        self.assertEqual(
            format_margin(Decimal("0.125")),
            "12,50%",
        )

    def test_formats_none_margin(self):
        self.assertEqual(format_margin(None), "--")

    def test_formats_naive_datetime(self):
        value = datetime(2026, 8, 25, 15, 30)
        self.assertEqual(
            format_datetime(value),
            "25/08/2026 15:30",
        )

    def test_formats_aware_datetime(self):
        value = datetime(
            2026,
            8,
            25,
            18,
            30,
            tzinfo=timezone.utc,
        )
        self.assertRegex(
            format_datetime(value),
            r"\d{2}/\d{2}/2026 \d{2}:30",
        )

    def test_labels_domain_enums(self):
        self.assertEqual(
            status_label(FreightStatus.IN_PROGRESS),
            "Em andamento",
        )
        self.assertEqual(
            event_label(FreightEventType.COMPLETED),
            "Concluído",
        )
        self.assertEqual(
            expense_label(FreightExpenseType.EMPILHADEIRA),
            "Empilhadeira",
        )
        self.assertEqual(
            vehicle_label(FreightVehicleType.CARRETA_LS),
            "Carreta LS",
        )

    def test_formats_yes_no_and_optional_text(self):
        self.assertEqual(yes_no(True), "Sim")
        self.assertEqual(yes_no(False), "Não")
        self.assertEqual(optional_text(None), "--")
        self.assertEqual(optional_text("   "), "--")
        self.assertEqual(optional_text("  teste  "), "teste")


if __name__ == "__main__":
    unittest.main()
