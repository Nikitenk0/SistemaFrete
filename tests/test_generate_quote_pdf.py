import unittest

from application.dtos.quote_document_data import (
    QuoteDocumentData
)
from application.exceptions import (
    QuotePdfGenerationError
)
from application.use_cases.generate_quote_pdf import (
    GenerateQuotePdf
)


class QuotePdfGeneratorFake:

    def __init__(
        self,
        error=None
    ):
        self.error = error
        self.document = None
        self.path = None

    def generate(
        self,
        document,
        path
    ) -> None:

        self.document = document
        self.path = path

        if self.error is not None:
            raise self.error


class TestGenerateQuotePdf(unittest.TestCase):

    def test_delega_geracao_ao_port(self):

        generator = QuotePdfGeneratorFake()

        use_case = GenerateQuotePdf(
            pdf_generator=generator
        )

        document = object()

        use_case.execute(
            document=document,
            path="orcamento.pdf"
        )

        self.assertIs(
            generator.document,
            document
        )

        self.assertEqual(
            generator.path,
            "orcamento.pdf"
        )

    def test_converte_falha_do_gerador(self):

        generator = QuotePdfGeneratorFake(
            error=RuntimeError(
                "Falha externa"
            )
        )

        use_case = GenerateQuotePdf(
            pdf_generator=generator
        )

        with self.assertRaises(
            QuotePdfGenerationError
        ):

            use_case.execute(
                document=object(),
                path="orcamento.pdf"
            )


if __name__ == "__main__":
    unittest.main()