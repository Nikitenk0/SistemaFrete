from tkinter import filedialog, messagebox

from application.ports.quote_pdf_generator import (
    QuotePdfGenerator
)
from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)
from domain.models.route_result import RouteResult


class OrcamentoPdfController:

    def __init__(
        self,
        gerador_pdf: QuotePdfGenerator
    ):
        self._gerador_pdf = gerador_pdf

    def gerar(
        self,
        resultado_rota: RouteResult,
        resultado_orcamento: QuoteCalculationResult,
        quantidade_eixos: int,
        calcular_volta: bool
    ) -> None:

        caminho = filedialog.asksaveasfilename(
            title="Salvar orçamento",
            defaultextension=".pdf",
            filetypes=[
                ("Arquivo PDF", "*.pdf")
            ],
            initialfile="orcamento.pdf"
        )

        if not caminho:
            return

        try:

            self._gerador_pdf.generate(
                route_result=resultado_rota,
                quote_result=resultado_orcamento,
                axle_count=quantidade_eixos,
                include_return_trip=calcular_volta,
                path=caminho
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                (
                    "Não foi possível gerar o PDF."
                    f"\n\n{erro}"
                )
            )

            return

        messagebox.showinfo(
            "Sucesso",
            "Orçamento gerado com sucesso!"
        )