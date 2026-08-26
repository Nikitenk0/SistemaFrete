import unittest
from decimal import Decimal

from presentation.desktop.freight_driver_amount_inputs import (
    parse_actual_driver_amount,
)


class FreightDriverAmountInputsTests(
    unittest.TestCase
):

    def test_parses_brazilian_currency(self):
        self.assertEqual(
            parse_actual_driver_amount(
                "R$ 2.345,67"
            ),
            Decimal("2345.67"),
        )

    def test_parses_dot_decimal(self):
        self.assertEqual(
            parse_actual_driver_amount(
                "2300.5"
            ),
            Decimal("2300.50"),
        )

    def test_accepts_zero(self):
        self.assertEqual(
            parse_actual_driver_amount("0"),
            Decimal("0.00"),
        )

    def test_rounds_to_two_decimal_places(self):
        self.assertEqual(
            parse_actual_driver_amount(
                "10,999"
            ),
            Decimal("11.00"),
        )

    def test_rejects_blank(self):
        with self.assertRaisesRegex(
            ValueError,
            "Informe o valor realizado"
        ):
            parse_actual_driver_amount("  ")

    def test_rejects_invalid_text(self):
        with self.assertRaisesRegex(
            ValueError,
            "Valor realizado inválido"
        ):
            parse_actual_driver_amount("abc")

    def test_rejects_negative(self):
        with self.assertRaisesRegex(
            ValueError,
            "Valor realizado inválido"
        ):
            parse_actual_driver_amount("-0,01")


if __name__ == "__main__":
    unittest.main()
