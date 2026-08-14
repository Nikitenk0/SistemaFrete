import unittest
from unittest.mock import patch

from domain.calculo.orcamento import calcular_orcamento


class TestCalculoOrcamento(unittest.TestCase):

    def test_calcula_orcamento_com_rctrc(self):

        with patch(
            "domain.calculo.orcamento.obter_aliquota_rctrc",
            return_value=0.10
        ) as obter_aliquota:

            resultado = calcular_orcamento(
                valor_nota=100000.0,
                geral=1000.0,
                pedagio=100.0,
                localizacao_origem="Rio Branco/Acre",
                localizacao_destino="Maceió/Alagoas"
            )

        obter_aliquota.assert_called_once_with(
            "Rio Branco/Acre",
            "Maceió/Alagoas"
        )

        self.assertEqual(
            resultado.valor_nota,
            100000.0
        )

        self.assertEqual(
            resultado.geral,
            1000.0
        )

        self.assertEqual(
            resultado.pedagio,
            100.0
        )

        self.assertEqual(
            resultado.custo,
            350.0
        )

        self.assertEqual(
            resultado.subtotal,
            1450.0
        )

        self.assertEqual(
            len(resultado.impostos),
            1
        )

        imposto = resultado.impostos[0]

        self.assertEqual(
            imposto.nome,
            "RCTRC"
        )

        self.assertEqual(
            imposto.aliquota,
            0.10
        )

        self.assertEqual(
            imposto.base_calculo,
            1450.0
        )

        self.assertEqual(
            imposto.valor,
            145.0
        )

        self.assertEqual(
            resultado.total_impostos,
            145.0
        )

        self.assertEqual(
            resultado.total,
            1595.0
        )


if __name__ == "__main__":
    unittest.main()