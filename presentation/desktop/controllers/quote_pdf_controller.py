from tkinter import filedialog, messagebox

from application.exceptions import (
    QuotePdfGenerationError
)
from application.use_cases.generate_quote_pdf import (
    GenerateQuotePdf
)
from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)
from application.dtos.route_result import RouteResult
from application.dtos.quote_document_data import (
    QuoteDocumentData
)

class QuotePdfController:

    def __init__(
        self,
        generate_quote_pdf: GenerateQuotePdf
    ):
        self._generate_quote_pdf = generate_quote_pdf

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

        document = QuoteDocumentData(
            route_result=route_result,
            quote_result=quote_result,
            axle_count=axle_count,
            include_return_trip=include_return_trip
        )

        try:

            self._generate_quote_pdf.execute(
                document=document,
                path=path
            )

        except QuotePdfGenerationError as error:

            messagebox.showerror(
                "Erro",
                str(error)
            )

            return

        messagebox.showinfo(
            "Sucesso",
            "Orçamento gerado com sucesso!"
        )