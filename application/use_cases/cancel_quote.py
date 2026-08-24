from dataclasses import replace
from datetime import (
    datetime,
    timezone
)

from application.exceptions import (
    InvalidQuoteDataError,
    InvalidQuoteStateError,
    QuoteNotFoundError
)
from application.ports.quote_unit_of_work import (
    QuoteUnitOfWorkFactory
)
from domain.models.quote import (
    Quote,
    QuoteStatus
)
from domain.models.quote_event import (
    QuoteEvent,
    QuoteEventType
)
from domain.models.quote_version import (
    QuoteVersion
)
from domain.quote_lifecycle import (
    validate_quote_transition
)


class CancelQuote:

    def __init__(
        self,
        quote_unit_of_work_factory:
            QuoteUnitOfWorkFactory
    ):
        self._quote_unit_of_work_factory = (
            quote_unit_of_work_factory
        )

    def execute(
        self,
        quote_id: int,
        reason: str,
        user_id: int | None = None
    ) -> Quote:

        cleaned_reason = reason.strip()

        if not cleaned_reason:
            raise InvalidQuoteDataError(
                "Cancelamento exige justificativa"
            )

        now = datetime.now(
            timezone.utc
        )

        with (
            self._quote_unit_of_work_factory.create()
            as unit_of_work
        ):

            quote = (
                unit_of_work.quotes
                .get_by_id_for_update(
                    quote_id
                )
            )

            if quote is None:
                raise QuoteNotFoundError(
                    "Orçamento não encontrado"
                )

            self._validate_transition(
                quote
            )

            version = self._latest_version(
                quote
            )

            cancellation_event = QuoteEvent(
                event_type=(
                    QuoteEventType.CANCELLED
                ),
                quote_version_id=(
                    version.quote_version_id
                ),
                previous_status=(
                    quote.current_status
                ),
                new_status=(
                    QuoteStatus.CANCELLED
                ),
                observation=cleaned_reason,
                user_id=user_id,
                occurred_at=now
            )

            updated_quote = replace(
                quote,
                current_status=(
                    QuoteStatus.CANCELLED
                ),
                events=(
                    *quote.events,
                    cancellation_event
                )
            )

            saved_quote = (
                unit_of_work.quotes.save(
                    updated_quote
                )
            )

            unit_of_work.commit()

            return saved_quote

    @staticmethod
    def _validate_transition(
        quote: Quote
    ) -> None:

        try:
            validate_quote_transition(
                quote.current_status,
                QuoteStatus.CANCELLED
            )
        except ValueError as error:
            raise InvalidQuoteStateError(
                str(error)
            ) from error

    @staticmethod
    def _latest_version(
        quote: Quote
    ) -> QuoteVersion:

        return max(
            quote.versions,
            key=lambda version: (
                version.version_number
            )
        )
