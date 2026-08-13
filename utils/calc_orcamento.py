from domain.calculo.orcamento import (
    calcular_orcamento as calcular_orcamento_dominio
)
from domain.models.resultado_orcamento import ResultadoOrcamento
from utils.conversao_monetaria import converter_valor_monetario


def calcular_orcamento(
    valor_nota,
    geral,
    pedagio,
    estado_origem,
    estado_destino
) -> ResultadoOrcamento:

    valor_nota_convertido = converter_valor_monetario(
        valor_nota
    )

    geral_convertido = converter_valor_monetario(
        geral
    )

    pedagio_convertido = converter_valor_monetario(
        pedagio
    )

    return calcular_orcamento_dominio(
        valor_nota=valor_nota_convertido,
        geral=geral_convertido,
        pedagio=pedagio_convertido,
        estado_origem=estado_origem,
        estado_destino=estado_destino
    )