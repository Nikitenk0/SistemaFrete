import unittest

from types import SimpleNamespace
from unittest.mock import (
    Mock,
    patch
)

from application.exceptions import (
    QuotePersistenceError
)
from infrastructure.persistence.sqlalchemy.quote_repository import (
    SqlAlchemyQuoteRepository
)


class QuoteRepositoryAuditWiringTests(
    unittest.TestCase
):

    def test_add_executes_aggregate_audit(
        self
    ) -> None:

        repository = SqlAlchemyQuoteRepository(
            Mock()
        )

        quote = SimpleNamespace(
            quote_id=None
        )

        with patch(
            (
                "infrastructure.persistence.sqlalchemy."
                "quote_repository."
                "validate_quote_audit_consistency"
            ),
            side_effect=ValueError(
                "Falha de auditoria"
            )
        ) as validator:

            with self.assertRaises(
                QuotePersistenceError
            ):
                repository.add(
                    quote
                )

            validator.assert_called_once_with(
                quote
            )

    def test_save_executes_aggregate_audit(
        self
    ) -> None:

        repository = SqlAlchemyQuoteRepository(
            Mock()
        )

        quote = SimpleNamespace(
            quote_id=1
        )

        with patch(
            (
                "infrastructure.persistence.sqlalchemy."
                "quote_repository."
                "validate_quote_audit_consistency"
            ),
            side_effect=ValueError(
                "Falha de auditoria"
            )
        ) as validator:

            with self.assertRaises(
                QuotePersistenceError
            ):
                repository.save(
                    quote
                )

            validator.assert_called_once_with(
                quote
            )


if __name__ == "__main__":
    unittest.main()