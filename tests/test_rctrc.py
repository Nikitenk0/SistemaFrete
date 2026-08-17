import unittest
from unittest.mock import patch

from domain.impostos.rctrc import get_rctrc_rate


class TestRCTRC(unittest.TestCase):

    def test_converte_codigo_estado_para_indice_da_matriz(self):
        matrix = [
            [0.0 for _ in range(27)]
            for _ in range(27)
        ]

        matrix[0][1] = 0.123

        with patch(
            "domain.impostos.rctrc.MATRIZ_RCTRC",
            matrix
        ):
            result = get_rctrc_rate(
                "Rio Branco/Acre",
                "Maceió/Alagoas"
            )

        self.assertEqual(
            result,
            0.123
        )

    def test_rejeita_localizacao_sem_estado(self):
        with self.assertRaises(ValueError):
            get_rctrc_rate(
                "Rio Branco",
                "Maceió/Alagoas"
            )


if __name__ == "__main__":
    unittest.main()