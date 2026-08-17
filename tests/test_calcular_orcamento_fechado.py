import unittest
from unittest.mock import patch

from application.exceptions import (
    InvalidQuoteDataError,
    QuoteCalculationError,
    RouteNotFoundError,
    RouteSearchError,
)
from application.use_cases.calculate_closed_load_quote import (
    CalculateClosedLoadQuote
)
from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)
from application.dtos.route_result import RouteResult


class RouteSearcherFake:

    def __init__(
        self,
        result=None,
        error=None
    ):
        self.result = result
        self.error = error
        self.search_args = None

    def search(
        self,
        origem,
        destino,
        quantidade_eixos,
        calcular_volta
    ):
        self.search_args = (
            origem,
            destino,
            quantidade_eixos,
            calcular_volta
        )

        if self.error is not None:
            raise self.error

        return self.result


class TestCalcularOrcamentoFechado(unittest.TestCase):

    def test_executa_fluxo_completo(self):

        route_result = RouteResult(
            origem="Rio Branco/Acre",
            destino="Maceió/Alagoas",
            distancia="300 km",
            pedagio="R$ 100,00",
            geral="R$ 1.000,00"
        )

        route_searcher = RouteSearcherFake(
            result=route_result
        )

        use_case = CalculateClosedLoadQuote(
            route_searcher=route_searcher
        )

        quote_calculation_result = QuoteCalculationResult(
            valor_nota=100000.0,
            geral=1000.0,
            pedagio=100.0,
            custo=350.0,
            subtotal=1450.0,
            impostos=(),
            total=1450.0
        )

        with patch(
            (
                "application.use_cases."
                "calculate_closed_load_quote."
                "calcular_orcamento"
            ),
            return_value=quote_calculation_result
        ) as calculate_quote_mock:

            result = use_case.execute(
                valor_nota="R$ 100.000,00",
                origem="Rio Branco",
                destino="Maceió",
                quantidade_eixos=6,
                calcular_volta=True
            )

        self.assertEqual(
            route_searcher.search_args,
            (
                "Rio Branco",
                "Maceió",
                6,
                True
            )
        )

        calculate_quote_mock.assert_called_once_with(
            valor_nota=100000.0,
            geral=1000.0,
            pedagio=100.0,
            localizacao_origem="Rio Branco/Acre",
            localizacao_destino="Maceió/Alagoas"
        )

        self.assertIs(
            result.route_result,
            route_result
        )

        self.assertIs(
            result.quote_result,
            quote_calculation_result
        )

    def test_rejeita_valor_da_nota_invalido(self):

        route_searcher = RouteSearcherFake()

        use_case = CalculateClosedLoadQuote(
            route_searcher=route_searcher
        )

        with self.assertRaises(
            InvalidQuoteDataError
        ):
            use_case.execute(
                valor_nota="valor inválido",
                origem="Rio Branco",
                destino="Maceió",
                quantidade_eixos=6,
                calcular_volta=False
            )

        self.assertIsNone(
            route_searcher.search_args
        )

    def test_converte_falha_da_pesquisa(self):

        route_searcher = RouteSearcherFake(
            error=RuntimeError(
                "Falha externa"
            )
        )

        use_case = CalculateClosedLoadQuote(
            route_searcher=route_searcher
        )

        with self.assertRaises(
            RouteSearchError
        ):
            use_case.execute(
                valor_nota="100000",
                origem="Rio Branco",
                destino="Maceió",
                quantidade_eixos=6,
                calcular_volta=False
            )

    def test_informa_rota_nao_encontrada(self):

        route_searcher = RouteSearcherFake(
            result=None
        )

        use_case = CalculateClosedLoadQuote(
            route_searcher=route_searcher
        )

        with self.assertRaises(
            RouteNotFoundError
        ):
            use_case.execute(
                valor_nota="100000",
                origem="Rio Branco",
                destino="Maceió",
                quantidade_eixos=6,
                calcular_volta=False
            )

    def test_converte_falha_do_calculo(self):

        route_result = RouteResult(
            origem="Rio Branco/Acre",
            destino="Maceió/Alagoas",
            distancia="300 km",
            pedagio="R$ 100,00",
            geral="R$ 1.000,00"
        )

        route_searcher = RouteSearcherFake(
            result=route_result
        )

        use_case = CalculateClosedLoadQuote(
            route_searcher=route_searcher
        )

        with patch(
            (
                "application.use_cases."
                "calculate_closed_load_quote."
                "calcular_orcamento"
            ),
            side_effect=RuntimeError(
                "Falha no cálculo"
            )
        ):

            with self.assertRaises(
                QuoteCalculationError
            ):
                use_case.execute(
                    valor_nota="100000",
                    origem="Rio Branco",
                    destino="Maceió",
                    quantidade_eixos=6,
                    calcular_volta=False
                )


if __name__ == "__main__":
    unittest.main()