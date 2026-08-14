import unittest

from utils.conversao_monetaria import converter_valor_monetario


class TestConversaoMonetaria(unittest.TestCase):

    def test_converte_formato_brasileiro(self):
        resultado = converter_valor_monetario(
            "R$ 6.143,83"
        )

        self.assertEqual(
            resultado,
            6143.83
        )

    def test_converte_separador_de_milhar(self):
        resultado = converter_valor_monetario(
            "150.000"
        )

        self.assertEqual(
            resultado,
            150000.0
        )

    def test_converte_numero_direto(self):
        resultado = converter_valor_monetario(
            150000
        )

        self.assertEqual(
            resultado,
            150000.0
        )

    def test_rejeita_valor_vazio(self):
        with self.assertRaises(ValueError):
            converter_valor_monetario("")


if __name__ == "__main__":
    unittest.main()