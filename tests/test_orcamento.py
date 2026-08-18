import unittest
from unittest.mock import patch
from decimal import Decimal
from domain.calculo.orcamento import calcular_orcamento


class TestCalculoOrcamento(unittest.TestCase):

    def test_calcula_orcamento_com_rctrc(self):

        with patch(
            "domain.calculo.orcamento.get_rctrc_rate",
            return_value=Decimal("0.10")
        ) as rctrc_rate_mock:

            result = calcular_orcamento(
                valor_nota=Decimal("100000.00"),
                geral=Decimal("1000.00"),
                pedagio=Decimal("100.00"),
                localizacao_origem="Rio Branco/Acre",
                localizacao_destino="Maceió/Alagoas"
            )

        rctrc_rate_mock.assert_called_once_with(
            "Rio Branco/Acre",
            "Maceió/Alagoas"
        )

        self.assertEqual(
            result.valor_nota,
            Decimal("100000.00")
        )

        self.assertEqual(
            result.geral,
            Decimal("1000.00")
        )

        self.assertEqual(
            result.pedagio,
            Decimal("100.00")
        )

        self.assertEqual(
            result.custo,
            Decimal("350.00")
        )

        self.assertEqual(
            result.subtotal,
            Decimal("1450.00")
        )

        self.assertEqual(
            len(result.impostos),
            1
        )

        imposto = result.impostos[0]

        self.assertEqual(
            imposto.nome,
            "RCTRC"
        )

        self.assertEqual(
            imposto.aliquota,
            Decimal("0.10")
        )

        self.assertEqual(
            imposto.base_calculo,
            Decimal("1450.00")
        )

        self.assertEqual(
            imposto.valor,
            Decimal("145.0000")
        )

        self.assertEqual(
            result.total_impostos,
            Decimal("145.0000")
        )

        self.assertEqual(
            result.total,
            Decimal("1595.0000")
        )


if __name__ == "__main__":
    unittest.main()