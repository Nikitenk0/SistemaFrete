from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

from domain.models.resultado_orcamento import ResultadoOrcamento
from domain.models.resultado_rota import ResultadoRota

def gerar_orcamento_pdf(
        resultado_rota: ResultadoRota,
        resultado_orcamento: ResultadoOrcamento,
        quantidade_eixos: int,
        calcular_volta: bool,
        caminho: str
    ):
    """

        Gera o PDF de um orçamento a partir dos resultados
        da rota e do cálculo financeiro.

    """

    pdf = canvas.Canvas(
        caminho,
        pagesize=A4
    )

    largura, altura = A4

    # ==========================================================
    # TÍTULO
    # ==========================================================

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawCentredString(
        largura / 2,
        altura - 3 * cm,
        "ORÇAMENTO"
    )

    # ==========================================================
    # DATA
    # ==========================================================

    pdf.setFont(
        "Helvetica",
        10
    )

    data = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    pdf.drawRightString(
        largura - 2 * cm,
        altura - 4 * cm,
        f"Data: {data}"
    )

    # ==========================================================
    # LINHA
    # ==========================================================

    pdf.line(
        2 * cm,
        altura - 4.5 * cm,
        largura - 2 * cm,
        altura - 4.5 * cm
    )
    # ==========================================================
    # DADOS DO ORÇAMENTO
    # ==========================================================

    y = altura - 6 * cm

    x_rotulo = 3 * cm
    x_valor = 7 * cm

    espacamento = 0.9 * cm


    def desenhar_linha(
        rotulo,
        valor,
        fonte_rotulo="Helvetica-Bold",
        fonte_valor="Helvetica",
        tamanho=12
    ):
        nonlocal y

        pdf.setFont(
            fonte_rotulo,
            tamanho
        )

        pdf.drawString(
            x_rotulo,
            y,
            rotulo
        )

        pdf.setFont(
            fonte_valor,
            tamanho
        )

        pdf.drawString(
            x_valor,
            y,
            str(valor)
        )

        y -= espacamento


    # ==========================================================
    # DADOS DA ROTA
    # ==========================================================

    desenhar_linha(
        "Origem:",
        resultado_rota.origem
    )

    desenhar_linha(
        "Destino:",
        resultado_rota.destino
    )

    desenhar_linha(
        "Distância:",
        resultado_rota.distancia
    )

    desenhar_linha(
        "Pedágio:",
        formatar_moeda(
            resultado_orcamento.pedagio
        )
    )

    desenhar_linha(
        "Quantidade de Eixos:",
        quantidade_eixos
    )

    texto_calcular_volta = (
        "Sim"
        if calcular_volta
        else "Não"
    )

    desenhar_linha(
        "Calcular Volta:",
        texto_calcular_volta
    )


    # ==========================================================
    # DADOS FINANCEIROS
    # ==========================================================

    y -= 0.5 * cm

    pdf.line(
        x_rotulo,
        y + 0.3 * cm,
        largura - 3 * cm,
        y + 0.3 * cm
    )

    desenhar_linha(
        "Valor da Nota:",
        formatar_moeda(
            resultado_orcamento.valor_nota
        )
    )

    desenhar_linha(
        "Geral:",
        formatar_moeda(
            resultado_orcamento.geral
        )
    )

    desenhar_linha(
        "Custo:",
        formatar_moeda(
            resultado_orcamento.custo
        )
    )


    # ==========================================================
    # IMPOSTOS
    # ==========================================================

    for imposto in resultado_orcamento.impostos:

        desenhar_linha(
            f"{imposto.nome}:",
            formatar_moeda(
                imposto.valor
            )
        )


    # ==========================================================
    # TOTAL
    # ==========================================================

    y -= 0.5 * cm

    pdf.line(
        x_rotulo,
        y + 0.3 * cm,
        largura - 3 * cm,
        y + 0.3 * cm
    )

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        x_rotulo,
        y,
        "TOTAL:"
    )

    pdf.drawString(
        x_valor,
        y,
        formatar_moeda(
            resultado_orcamento.total
        )
    )
    # ==========================================================
    # FINALIZA
    # ==========================================================

    pdf.save()

def formatar_moeda(valor: float) -> str:

    valor_formatado = (
        f"{valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {valor_formatado}"