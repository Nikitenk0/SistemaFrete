from domain.calculo.custo import calcular_custo
from domain.impostos.rctrc import obter_aliquota_rctrc
from domain.models.imposto_calculado import ImpostoCalculado
from domain.models.resultado_orcamento import ResultadoOrcamento


def calcular_orcamento(
    valor_nota: float,
    geral: float,
    pedagio: float,
    estado_origem: str,
    estado_destino: str
) -> ResultadoOrcamento:

    custo = calcular_custo(
        valor_nota
    )

    aliquota_rctrc = obter_aliquota_rctrc(
        estado_origem,
        estado_destino
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

    imposto_rctrc = ImpostoCalculado(
        nome="RCTRC",
        aliquota=aliquota_rctrc,
        base_calculo=subtotal,
        valor=valor_rctrc
    )

    total = (
        subtotal
        + valor_rctrc
    )

    return ResultadoOrcamento(
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