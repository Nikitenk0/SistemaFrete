import unittest

from domain.calculo.custo import calcular_custo


class TestCalculoCusto(unittest.TestCase):

    def test_custo_no_limite(self):
        resultado = calcular_custo(
            200000
        )

        self.assertEqual(
            resultado,
            350.0
        )

    def test_custo_abaixo_do_limite(self):
        resultado = calcular_custo(
            199999
        )

        self.assertEqual(
            resultado,
            350.0
        )

    def test_custo_acima_do_limite(self):
        resultado = calcular_custo(
            200001
        )

        self.assertEqual(
            resultado,
            550.0
        )


if __name__ == "__main__":
    unittest.main()