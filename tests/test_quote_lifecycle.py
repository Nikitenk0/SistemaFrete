import unittest

from domain.models.quote import (
    QuoteStatus
)
from domain.quote_lifecycle import (
    can_transition_quote,
    validate_quote_transition
)


class TestQuoteLifecycle(unittest.TestCase):

    def test_allows_expected_main_flow(
        self
    ):

        self.assertTrue(
            can_transition_quote(
                QuoteStatus.DRAFT,
                QuoteStatus.CALCULATED
            )
        )

        self.assertTrue(
            can_transition_quote(
                QuoteStatus.CALCULATED,
                QuoteStatus.OFFERED
            )
        )

        self.assertTrue(
            can_transition_quote(
                QuoteStatus.OFFERED,
                QuoteStatus.NEGOTIATION
            )
        )

        self.assertTrue(
            can_transition_quote(
                QuoteStatus.NEGOTIATION,
                QuoteStatus.APPROVED
            )
        )

    def test_rejects_transition_from_terminal_status(
        self
    ):

        with self.assertRaises(ValueError):
            validate_quote_transition(
                QuoteStatus.APPROVED,
                QuoteStatus.CALCULATED
            )


if __name__ == "__main__":
    unittest.main()
