from typing import Protocol

from application.dtos.quote_document_data import (
    QuoteDocumentData
)


class QuotePdfGenerator(Protocol):

    def generate(
        self,
        document: QuoteDocumentData,
        path: str
    ) -> None:
        ...