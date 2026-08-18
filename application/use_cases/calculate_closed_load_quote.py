import logging
from decimal import Decimal
from application.dtos.closed_load_quote_result import (
    ClosedLoadQuoteResult
)
from application.ports.route_searcher import RouteSearcher
from application.exceptions import (
    InvalidQuoteDataError,
    QuoteCalculationError,
    RouteNotFoundError,
    RouteSearchError,
)
from domain.calculo.orcamento import calcular_orcamento
from application.parsers.monetary_value import parse_monetary_value

logger = logging.getLogger(
    "sistemafrete.application.calculate_closed_load_quote"
)

class CalculateClosedLoadQuote:

    def __init__(
        self,
        route_searcher: RouteSearcher
    ):
        self._route_searcher = route_searcher

    def execute(
        self,
        valor_nota: str | int | float | Decimal,
        origem: str,
        destino: str,
        quantidade_eixos: int,
        calcular_volta: bool
    ) -> ClosedLoadQuoteResult:

        try:
            valor_nota_convertido = parse_monetary_value(
                valor_nota
            )

        except ValueError as error:
            raise InvalidQuoteDataError(
                "Valor da nota inválido"
            ) from error

        try:
            route_result = self._route_searcher.search(
                origem,
                destino,
                quantidade_eixos,
                calcular_volta
            )

        except Exception as error:

            logger.exception(
                "Falha técnica ao pesquisar rota"
            )

            raise RouteSearchError(
                "Não foi possível pesquisar a rota"
            ) from error

        if route_result is None:
            raise RouteNotFoundError(
                "Nenhuma rota encontrada"
            )

        try:
            geral = parse_monetary_value(
                route_result.geral
            )

            pedagio = parse_monetary_value(
                route_result.pedagio
            )

            quote_calculation_result = calcular_orcamento(
                valor_nota=valor_nota_convertido,
                geral=geral,
                pedagio=pedagio,
                localizacao_origem=route_result.origem,
                localizacao_destino=route_result.destino
            )

        except Exception as error:

            logger.exception(
                "Falha técnica ao calcular orçamento"
            )

            raise QuoteCalculationError(
                "Não foi possível calcular o orçamento"
            ) from error

        return ClosedLoadQuoteResult(
            route_result=route_result,
            quote_result=quote_calculation_result
        )
