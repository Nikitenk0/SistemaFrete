from dataclasses import replace
from datetime import (
    datetime,
    timezone
)

from application.exceptions import (
    InvalidQuoteStateError,
    QuoteConcurrentModificationError,
    QuoteNotFoundError
)
from application.ports.quote_unit_of_work import (
    QuoteUnitOfWorkFactory
)
from application.ports.quote_version_calculator import (
    QuoteVersionCalculator
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


class CalculateQuote:

    def __init__(
        self,
        quote_unit_of_work_factory:
            QuoteUnitOfWorkFactory,
        quote_version_calculator:
            QuoteVersionCalculator
    ):
        self._quote_unit_of_work_factory = (
            quote_unit_of_work_factory
        )
        self._quote_version_calculator = (
            quote_version_calculator
        )

    def execute(
        self,
        quote_id: int,
        user_id: int | None = None
    ) -> Quote:

        original_quote = self._load_quote(
            quote_id
        )

        self._validate_can_calculate(
            original_quote
        )

        original_version = self._latest_version(
            original_quote
        )

        calculated_version = (
            self._quote_version_calculator.execute(
                original_version
            )
        )

        now = datetime.now(
            timezone.utc
        )

        with (
            self._quote_unit_of_work_factory.create()
            as unit_of_work
        ):

            current_quote = (
                unit_of_work.quotes
                .get_by_id_for_update(
                    quote_id
                )
            )

            if current_quote is None:
                raise QuoteNotFoundError(
                    "Orçamento não encontrado"
                )

            if current_quote != original_quote:
                raise QuoteConcurrentModificationError(
                    "O orçamento foi alterado "
                    "durante o cálculo. Recarregue "
                    "os dados e calcule novamente."
                )

            current_version = self._latest_version(
                current_quote
            )

            if (
                current_version.quote_version_id
                != calculated_version.quote_version_id
                or current_version.version_number
                != calculated_version.version_number
            ):
                raise QuoteConcurrentModificationError(
                    "A versão atual do orçamento "
                    "mudou durante o cálculo"
                )

            updated_versions = tuple(
                calculated_version
                if version.quote_version_id
                == current_version.quote_version_id
                else version
                for version in current_quote.versions
            )

            previous_status = (
                current_quote.current_status
            )

            if previous_status == QuoteStatus.DRAFT:
                try:
                    validate_quote_transition(
                        previous_status,
                        QuoteStatus.CALCULATED
                    )
                except ValueError as error:
                    raise InvalidQuoteStateError(
                        str(error)
                    ) from error

            calculated_event = QuoteEvent(
                event_type=(
                    QuoteEventType.CALCULATED
                ),
                quote_version_id=(
                    current_version.quote_version_id
                ),
                previous_status=previous_status,
                new_status=QuoteStatus.CALCULATED,
                user_id=user_id,
                occurred_at=now
            )

            updated_quote = replace(
                current_quote,
                current_status=(
                    QuoteStatus.CALCULATED
                ),
                versions=updated_versions,
                events=(
                    *current_quote.events,
                    calculated_event
                )
            )

            saved_quote = (
                unit_of_work.quotes.save(
                    updated_quote
                )
            )

            unit_of_work.commit()

            return saved_quote

    def _load_quote(
        self,
        quote_id: int
    ) -> Quote:

        with (
            self._quote_unit_of_work_factory.create()
            as unit_of_work
        ):

            quote = unit_of_work.quotes.get_by_id(
                quote_id
            )

            if quote is None:
                raise QuoteNotFoundError(
                    "Orçamento não encontrado"
                )

            return quote

    @staticmethod
    def _validate_can_calculate(
        quote: Quote
    ) -> None:

        if quote.current_status not in (
            QuoteStatus.DRAFT,
            QuoteStatus.CALCULATED
        ):
            raise InvalidQuoteStateError(
                "Somente orçamento em rascunho "
                "ou calculado pode ser calculado "
                "novamente"
            )

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
