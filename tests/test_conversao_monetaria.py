import unittest

from application.parsers.monetary_value import parse_monetary_value


class TestConversaoMonetaria(unittest.TestCase):

    def test_converte_formato_brasileiro(self):
        result = parse_monetary_value(
            "R$ 6.143,83"
        )

        self.assertEqual(
            result,
            6143.83
        )

    def test_converte_separador_de_milhar(self):
        result = parse_monetary_value(
            "150.000"
        )

        self.assertEqual(
            result,
            150000.0
        )

    def test_converte_numero_direto(self):
        result = parse_monetary_value(
            150000
        )

        self.assertEqual(
            result,
            150000.0
        )

    def test_rejeita_valor_vazio(self):
        with self.assertRaises(ValueError):
            parse_monetary_value("")


if __name__ == "__main__":
    unittest.main()