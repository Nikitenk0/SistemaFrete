from tkinter import filedialog, messagebox

from application.ports.quote_pdf_generator import (
    QuotePdfGenerator
)
from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)
from domain.models.route_result import RouteResult


class QuotePdfController:

    def __init__(
        self,
        pdf_generator: QuotePdfGenerator
    ):
        self._pdf_generator = pdf_generator

    def generate(
        self,
        route_result: RouteResult,
        quote_result: QuoteCalculationResult,
        axle_count: int,
        include_return_trip: bool
    ) -> None:

        path = filedialog.asksaveasfilename(
            title="Salvar orçamento",
            defaultextension=".pdf",
            filetypes=[
                ("Arquivo PDF", "*.pdf")
            ],
            initialfile="orcamento.pdf"
        )

        if not path:
            return

        try:

            self._pdf_generator.generate(
                route_result=route_result,
                quote_result=quote_result,
                axle_count=axle_count,
                include_return_trip=include_return_trip,
                path=path
            )

        except Exception as error:

            messagebox.showerror(
                "Erro",
                (
                    "Não foi possível gerar o PDF."
                    f"\n\n{error}"
                )
            )

            return

        messagebox.showinfo(
            "Sucesso",
            "Orçamento gerado com sucesso!"
        )