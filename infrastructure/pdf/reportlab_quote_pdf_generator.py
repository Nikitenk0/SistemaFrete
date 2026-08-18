from datetime import datetime
from decimal import Decimal

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from application.dtos.quote_document_data import (
    QuoteDocumentData
)


class ReportLabQuotePdfGenerator:

    def generate(
        self,
        document: QuoteDocumentData,
        path: str
    ) -> None:

        pdf = canvas.Canvas(
            path,
            pagesize=A4
        )

        width, height = A4

        y = self._draw_header(
            pdf=pdf,
            document=document,
            width=width,
            height=height
        )

        y = self._draw_customer_section(
            pdf=pdf,
            document=document,
            width=width,
            y=y
        )

        y = self._draw_route_section(
            pdf=pdf,
            document=document,
            width=width,
            y=y
        )

        y = self._draw_financial_section(
            pdf=pdf,
            document=document,
            width=width,
            y=y
        )

        self._draw_total(
            pdf=pdf,
            document=document,
            width=width,
            y=y
        )

        pdf.save()

    def _draw_header(
        self,
        pdf,
        document: QuoteDocumentData,
        width,
        height
    ):

        pdf.setFont(
            "Helvetica-Bold",
            20
        )

        pdf.drawCentredString(
            width / 2,
            height - 3 * cm,
            "ORÇAMENTO"
        )

        issued_at = (
            document.issued_at
            if document.issued_at is not None
            else datetime.now()
        )

        pdf.setFont(
            "Helvetica",
            10
        )

        pdf.drawRightString(
            width - 2 * cm,
            height - 4 * cm,
            (
                "Data: "
                + issued_at.strftime(
                    "%d/%m/%Y %H:%M"
                )
            )
        )

        if document.quote_number:

            pdf.drawString(
                2 * cm,
                height - 4 * cm,
                (
                    "Orçamento: "
                    + document.quote_number
                )
            )

        pdf.line(
            2 * cm,
            height - 4.5 * cm,
            width - 2 * cm,
            height - 4.5 * cm
        )

        return height - 6 * cm

    def _draw_customer_section(
        self,
        pdf,
        document: QuoteDocumentData,
        width,
        y
    ):

        customer = document.customer

        if customer is None:
            return y

        if (
            not customer.name
            and not customer.cnpj
        ):
            return y

        y = self._draw_section_title(
            pdf=pdf,
            title="CLIENTE",
            width=width,
            y=y
        )

        if customer.name:

            y = self._draw_line(
                pdf=pdf,
                y=y,
                label="Nome:",
                value=customer.name
            )

        if customer.cnpj:

            y = self._draw_line(
                pdf=pdf,
                y=y,
                label="CNPJ:",
                value=customer.cnpj
            )

        return y - 0.3 * cm

    def _draw_route_section(
        self,
        pdf,
        document: QuoteDocumentData,
        width,
        y
    ):

        route = document.route_result


        y = self._draw_section_title(
            pdf=pdf,
            title="ROTA",
            width=width,
            y=y
        )

        y = self._draw_line(
            pdf=pdf,
            y=y,
            label="Origem:",
            value=route.origem
        )

        y = self._draw_line(
            pdf=pdf,
            y=y,
            label="Destino:",
            value=route.destino
        )

        y = self._draw_line(
            pdf=pdf,
            y=y,
            label="Distância:",
            value=route.distancia
        )

        y = self._draw_line(
            pdf=pdf,
            y=y,
            label="Quant. de Eixos:",
            value=document.axle_count
        )

        return_trip_text = (
            "Sim"
            if document.include_return_trip
            else "Não"
        )

        y = self._draw_line(
            pdf=pdf,
            y=y,
            label="Calcular Volta:",
            value=return_trip_text
        )

        return y - 0.3 * cm

    def _draw_financial_section(
        self,
        pdf,
        document: QuoteDocumentData,
        width,
        y
    ):

        quote = document.quote_result

        y = self._draw_section_title(
            pdf=pdf,
            title="VALORES",
            width=width,
            y=y
        )

        y = self._draw_line(
            pdf=pdf,
            y=y,
            label="Valor da Nota:",
            value=self._format_currency(
                quote.valor_nota
            )
        )

        y = self._draw_line(
            pdf=pdf,
            y=y,
            label="Geral:",
            value=self._format_currency(
                quote.geral
            )
        )

        y = self._draw_line(
            pdf=pdf,
            y=y,
            label="Pedágio:",
            value=self._format_currency(
                quote.pedagio
            )
        )

        y = self._draw_line(
            pdf=pdf,
            y=y,
            label="Custo:",
            value=self._format_currency(
                quote.custo
            )
        )

        for tax in quote.impostos:

            y = self._draw_line(
                pdf=pdf,
                y=y,
                label=f"{tax.nome}:",
                value=self._format_currency(
                    tax.valor
                )
            )

        return y

    def _draw_total(
        self,
        pdf,
        document: QuoteDocumentData,
        width,
        y
    ) -> None:

        quote = document.quote_result

        y -= 0.4 * cm

        pdf.line(
            3 * cm,
            y + 0.3 * cm,
            width - 3 * cm,
            y + 0.3 * cm
        )

        pdf.setFont(
            "Helvetica-Bold",
            14
        )

        pdf.drawString(
            3 * cm,
            y,
            "TOTAL:"
        )

        pdf.drawString(
            7 * cm,
            y,
            self._format_currency(
                quote.total
            )
        )

    @staticmethod
    def _draw_section_title(
        pdf,
        title: str,
        width,
        y
    ):

        pdf.setFont(
            "Helvetica-Bold",
            11
        )

        pdf.drawString(
            3 * cm,
            y,
            title
        )

        pdf.line(
            3 * cm,
            y - 0.15 * cm,
            width - 3 * cm,
            y - 0.15 * cm
        )

        return y - 0.7 * cm

    @staticmethod
    def _draw_line(
        pdf,
        y,
        label,
        value,
        label_font="Helvetica-Bold",
        value_font="Helvetica",
        font_size=12
    ):

        pdf.setFont(
            label_font,
            font_size
        )

        pdf.drawString(
            3 * cm,
            y,
            label
        )

        pdf.setFont(
            value_font,
            font_size
        )

        pdf.drawString(
            7 * cm,
            y,
            str(value)
        )

        return y - 0.9 * cm

    @staticmethod
    def _format_currency(
        value: Decimal
    ) -> str:

        formatted_value = (
            f"{value:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return f"R$ {formatted_value}"