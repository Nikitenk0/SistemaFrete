import unittest
from unittest.mock import patch

from domain.impostos.rctrc import obter_aliquota_rctrc


class TestRCTRC(unittest.TestCase):

    def test_converte_codigo_estado_para_indice_da_matriz(self):
        matriz = [
            [0.0 for _ in range(27)]
            for _ in range(27)
        ]

        matriz[0][1] = 0.123

        with patch(
            "domain.impostos.rctrc.MATRIZ_RCTRC",
            matriz
        ):
            resultado = obter_aliquota_rctrc(
                "Rio Branco/Acre",
                "Maceió/Alagoas"
            )

        self.assertEqual(
            resultado,
            0.123
        )

    def test_rejeita_localizacao_sem_estado(self):
        with self.assertRaises(ValueError):
            obter_aliquota_rctrc(
                "Rio Branco",
                "Maceió/Alagoas"
            )


if __name__ == "__main__":
    unittest.main()