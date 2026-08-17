from domain.calculo.custo import calcular_custo
from domain.impostos.rctrc import get_rctrc_rate
from domain.models.calculated_tax import CalculatedTax
from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)


def calcular_orcamento(
    valor_nota: float,
    geral: float,
    pedagio: float,
    localizacao_origem: str,
    localizacao_destino: str
) -> QuoteCalculationResult:

    custo = calcular_custo(
        valor_nota
    )

    aliquota_rctrc = get_rctrc_rate(
        localizacao_origem,
        localizacao_destino
    )

    subtotal = (
        geral
        + pedagio
        + custo
    )

    valor_rctrc = (
        subtotal
        * aliquota_rctrc
    )

    imposto_rctrc = CalculatedTax(
        nome="RCTRC",
        aliquota=aliquota_rctrc,
        base_calculo=subtotal,
        valor=valor_rctrc
    )

    total = (
        subtotal
        + valor_rctrc
    )

    return QuoteCalculationResult(
        valor_nota=valor_nota,
        geral=geral,
        pedagio=pedagio,
        custo=custo,
        subtotal=subtotal,
        impostos=(
            imposto_rctrc,
        ),
        total=total
    )