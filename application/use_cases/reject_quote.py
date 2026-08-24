import re

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


class RejectQuote:

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
        reason_code: str,
        observation: str | None = None,
        user_id: int | None = None
    ) -> Quote:

        normalized_reason_code = (
            self._normalize_reason_code(
                reason_code
            )
        )

        cleaned_observation = (
            self._clean_optional_text(
                observation
            )
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

            if (
                version.quote_version_id is None
                or version.offered_price is None
            ):
                raise InvalidQuoteDataError(
                    "Recusa exige uma versão "
                    "ofertada e persistida"
                )

            rejection_event = QuoteEvent(
                event_type=(
                    QuoteEventType.REJECTED
                ),
                quote_version_id=(
                    version.quote_version_id
                ),
                previous_status=(
                    quote.current_status
                ),
                new_status=(
                    QuoteStatus.REJECTED
                ),
                previous_amount=(
                    version.offered_price
                ),
                reason_code=(
                    normalized_reason_code
                ),
                observation=(
                    cleaned_observation
                ),
                user_id=user_id,
                occurred_at=now
            )

            updated_quote = replace(
                quote,
                current_status=(
                    QuoteStatus.REJECTED
                ),
                events=(
                    *quote.events,
                    rejection_event
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
                QuoteStatus.REJECTED
            )
        except ValueError as error:
            raise InvalidQuoteStateError(
                str(error)
            ) from error

    @staticmethod
    def _normalize_reason_code(
        value: str
    ) -> str:

        normalized = value.strip().upper()

        if not normalized:
            raise InvalidQuoteDataError(
                "Motivo estruturado da recusa é obrigatório"
            )

        if len(normalized) > 100:
            raise InvalidQuoteDataError(
                "Código do motivo da recusa é muito longo"
            )

        if not re.fullmatch(
            r"[A-Z0-9][A-Z0-9_-]*",
            normalized
        ):
            raise InvalidQuoteDataError(
                "Código do motivo da recusa é inválido"
            )

        return normalized

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

    @staticmethod
    def _clean_optional_text(
        value: str | None
    ) -> str | None:

        if value is None:
            return None

        cleaned_value = value.strip()

        return (
            cleaned_value
            if cleaned_value
            else None
        )
