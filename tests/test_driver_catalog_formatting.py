import unittest
from datetime import date

from domain.models.driver import DriverStatus
from presentation.desktop.driver_catalog_formatting import (
    DRIVER_STATUS_OPTIONS,
    driver_status_label,
    format_driver_cpf,
    format_driver_date,
    format_driver_phone,
)


class DriverCatalogFormattingTests(unittest.TestCase):

    def test_formats_cpf(self):
        self.assertEqual(
            format_driver_cpf("12345678901"),
            "123.456.789-01",
        )

    def test_formats_mobile_phone(self):
        self.assertEqual(
            format_driver_phone("41999998888"),
            "(41) 99999-8888",
        )

    def test_formats_landline_phone(self):
        self.assertEqual(
            format_driver_phone("4133334444"),
            "(41) 3333-4444",
        )

    def test_formats_missing_phone(self):
        self.assertEqual(format_driver_phone(None), "--")

    def test_formats_date_and_status(self):
        self.assertEqual(
            format_driver_date(date(2030, 5, 20)),
            "20/05/2030",
        )
        self.assertEqual(
            driver_status_label(DriverStatus.ACTIVE),
            "Ativo",
        )
        self.assertEqual(
            driver_status_label(DriverStatus.INACTIVE),
            "Inativo",
        )

    def test_status_options(self):
        self.assertIsNone(DRIVER_STATUS_OPTIONS["Todos"])
        self.assertEqual(
            DRIVER_STATUS_OPTIONS["Ativos"],
            DriverStatus.ACTIVE,
        )
        self.assertEqual(
            DRIVER_STATUS_OPTIONS["Inativos"],
            DriverStatus.INACTIVE,
        )


if __name__ == "__main__":
    unittest.main()
