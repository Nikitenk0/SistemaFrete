import unittest

from domain.calculo.custo import calcular_custo


class TestCalculoCusto(unittest.TestCase):

    def test_custo_no_limite(self):
        result = calcular_custo(
            200000
        )

        self.assertEqual(
            result,
            350.0
        )

    def test_custo_abaixo_do_limite(self):
        result = calcular_custo(
            199999
        )

        self.assertEqual(
            result,
            350.0
        )

    def test_custo_acima_do_limite(self):
        result = calcular_custo(
            200001
        )

        self.assertEqual(
            result,
            550.0
        )


if __name__ == "__main__":
    unittest.main()