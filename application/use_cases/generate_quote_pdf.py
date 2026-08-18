import logging
from application.dtos.quote_document_data import (
    QuoteDocumentData
)
from application.exceptions import (
    QuotePdfGenerationError
)
from application.ports.quote_pdf_generator import (
    QuotePdfGenerator
)

logger = logging.getLogger(
    "sistemafrete.application.generate_quote_pdf"
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

            logger.exception(
                "Falha técnica ao gerar PDF"
            )

            raise QuotePdfGenerationError(
                "Não foi possível gerar o PDF"
            ) from error