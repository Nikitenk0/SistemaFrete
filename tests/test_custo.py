import unittest
from decimal import Decimal
from domain.calculo.custo import calcular_custo


class TestCalculoCusto(unittest.TestCase):

    def test_custo_no_limite(self):
        result = calcular_custo(
            Decimal("200000")
        )

        self.assertEqual(
            result,
            Decimal("350.00")
        )

    def test_custo_abaixo_do_limite(self):
        result = calcular_custo(
            Decimal("199999")
        )

        self.assertEqual(
            result,
            Decimal("350.00")
        )

    def test_custo_acima_do_limite(self):
        result = calcular_custo(
            Decimal("200001")
        )

        self.assertEqual(
            result,
            Decimal("550.00")
        )


if __name__ == "__main__":
    unittest.main()