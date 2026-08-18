from application.dtos.quote_document_data import (
    QuoteDocumentData
)
from application.exceptions import (
    QuotePdfGenerationError
)
from application.ports.quote_pdf_generator import (
    QuotePdfGenerator
)


class GenerateQuotePdf:

    def __init__(
        self,
        pdf_generator: QuotePdfGenerator
    ):
        self._pdf_generator = pdf_generator

    def execute(
        self,
        document: QuoteDocumentData,
        path: str
    ) -> None:

        try:

            self._pdf_generator.generate(
                document=document,
                path=path
            )

        except Exception as error:

            raise QuotePdfGenerationError(
                "Não foi possível gerar o PDF"
            ) from error