from typing import Protocol

from domain.models.quote_version import (
    QuoteVersion
)


class QuoteVersionCalculator(Protocol):

    def execute(
        self,
        version: QuoteVersion
    ) -> QuoteVersion:
        ...
