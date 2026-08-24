from typing import Protocol


class QuoteNumberGenerator(Protocol):

    def next_number(
        self,
        year: int
    ) -> str:
        ...