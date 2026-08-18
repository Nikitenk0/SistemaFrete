from datetime import datetime
from decimal import Decimal
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)
from application.dtos.route_result import RouteResult

def generate_quote_pdf(
    route_result: RouteResult,
    quote_result: QuoteCalculationResult,
    axle_count: int,
    include_return_trip: bool,
    path: str
):
    """

        Gera o PDF de um orçamento a partir dos resultados
        da rota e do cálculo financeiro.

    """

    pdf = canvas.Canvas(
        path,
        pagesize=A4
    )

    width, height = A4

    # ==========================================================
    # TÍTULO
    # ==========================================================

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawCentredString(
        width / 2,
        height - 3 * cm,
        "ORÇAMENTO"
    )

    # ==========================================================
    # DATA
    # ==========================================================

    pdf.setFont(
        "Helvetica",
        10
    )

    generated_at = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    pdf.drawRightString(
        width - 2 * cm,
        height - 4 * cm,
        f"Data: {generated_at}"
    )

    # ==========================================================
    # LINHA
    # ==========================================================

    pdf.line(
        2 * cm,
        height - 4.5 * cm,
        width - 2 * cm,
        height - 4.5 * cm
    )
    # ==========================================================
    # DADOS DO ORÇAMENTO
    # ==========================================================

    y = height - 6 * cm

    label_x = 3 * cm
    value_x = 7 * cm

    line_spacing = 0.9 * cm


    def draw_line(
        label,
        value,
        label_font="Helvetica-Bold",
        value_font="Helvetica",
        font_size=12
    ):
        nonlocal y

        pdf.setFont(
            label_font,
            font_size
        )

        pdf.drawString(
            label_x,
            y,
            label
        )

        pdf.setFont(
            value_font,
            font_size
        )

        pdf.drawString(
            value_x,
            y,
            str(value)
        )

        y -= line_spacing


    # ==========================================================
    # DADOS DA ROTA
    # ==========================================================

    draw_line(
        "Origem:",
        route_result.origem
    )

    draw_line(
        "Destino:",
        route_result.destino
    )

    draw_line(
        "Distância:",
        route_result.distancia
    )

    draw_line(
        "Pedágio:",
        format_currency(
            quote_result.pedagio
        )
    )

    draw_line(
        "Quant. de Eixos:",
        axle_count
    )

    return_trip_text = (
        "Sim"
        if include_return_trip
        else "Não"
    )

    draw_line(
        "Calcular Volta:",
        return_trip_text
    )


    # ==========================================================
    # DADOS FINANCEIROS
    # ==========================================================

    y -= 0.5 * cm

    pdf.line(
        label_x,
        y + 0.3 * cm,
        width - 3 * cm,
        y + 0.3 * cm
    )

    draw_line(
        "Valor da Nota:",
        format_currency(
            quote_result.valor_nota
        )
    )

    draw_line(
        "Geral:",
        format_currency(
            quote_result.geral
        )
    )

    draw_line(
        "Custo:",
        format_currency(
            quote_result.custo
        )
    )


    # ==========================================================
    # IMPOSTOS
    # ==========================================================

    for tax in quote_result.impostos:

        draw_line(
            f"{tax.nome}:",
            format_currency(
                tax.valor
            )
        )


    # ==========================================================
    # TOTAL
    # ==========================================================

    y -= 0.5 * cm

    pdf.line(
        label_x,
        y + 0.3 * cm,
        width - 3 * cm,
        y + 0.3 * cm
    )

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        label_x,
        y,
        "TOTAL:"
    )

    pdf.drawString(
        value_x,
        y,
        format_currency(
            quote_result.total
        )
    )
    # ==========================================================
    # FINALIZA
    # ==========================================================

    pdf.save()

def format_currency(
        value: Decimal
    ) -> str:

    formatted_value = (
        f"{value:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {formatted_value}"

class ReportLabQuotePdfGenerator:

    def generate(
        self,
        route_result: RouteResult,
        quote_result: QuoteCalculationResult,
        axle_count: int,
        include_return_trip: bool,
        path: str
    ) -> None:

        generate_quote_pdf(
            route_result=route_result,
            quote_result=quote_result,
            axle_count=axle_count,
            include_return_trip=include_return_trip,
            path=path
        )