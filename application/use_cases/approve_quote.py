from dataclasses import replace
from datetime import (
    datetime,
    timezone
)
from decimal import Decimal

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
from domain.pricing.effective_margin import (
    calculate_effective_margin
)
from domain.quote_lifecycle import (
    validate_quote_transition
)


class ApproveQuote:

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
        contracted_price: Decimal,
        price_change_reason: str | None = None,
        acceptance_observation: str | None = None,
        user_id: int | None = None
    ) -> Quote:

        if contracted_price < 0:
            raise InvalidQuoteDataError(
                "Preço contratado não pode ser negativo"
            )

        cleaned_price_change_reason = (
            self._clean_optional_text(
                price_change_reason
            )
        )

        cleaned_acceptance_observation = (
            self._clean_optional_text(
                acceptance_observation
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

            self._validate_offered_version(
                version
            )

            offered_price = version.offered_price

            if offered_price is None:
                raise InvalidQuoteDataError(
                    "Versão negociada não possui "
                    "preço ofertado"
                )

            if (
                contracted_price != offered_price
                and not cleaned_price_change_reason
            ):
                raise InvalidQuoteDataError(
                    "Alteração do preço contratado "
                    "exige justificativa"
                )

            try:
                (
                    contracted_margin_value,
                    contracted_margin_rate
                ) = calculate_effective_margin(
                    gross_price=contracted_price,
                    bp02=version.bp02,
                    tax_rate=version.tax_rate
                )
            except ValueError as error:
                raise InvalidQuoteDataError(
                    str(error)
                ) from error

            updated_version = replace(
                version,
                contracted_price=(
                    contracted_price
                ),
                contracted_margin_value=(
                    contracted_margin_value
                ),
                contracted_margin_rate=(
                    contracted_margin_rate
                )
            )

            events = list(
                quote.events
            )

            if contracted_price != offered_price:
                events.append(
                    QuoteEvent(
                        event_type=(
                            QuoteEventType.PRICE_CHANGED
                        ),
                        quote_version_id=(
                            version.quote_version_id
                        ),
                        previous_amount=(
                            offered_price
                        ),
                        new_amount=(
                            contracted_price
                        ),
                        observation=(
                            cleaned_price_change_reason
                        ),
                        user_id=user_id,
                        occurred_at=now
                    )
                )

            events.append(
                QuoteEvent(
                    event_type=(
                        QuoteEventType.APPROVED
                    ),
                    quote_version_id=(
                        version.quote_version_id
                    ),
                    previous_status=(
                        quote.current_status
                    ),
                    new_status=(
                        QuoteStatus.APPROVED
                    ),
                    previous_amount=(
                        offered_price
                    ),
                    new_amount=(
                        contracted_price
                    ),
                    observation=(
                        cleaned_acceptance_observation
                    ),
                    user_id=user_id,
                    occurred_at=now
                )
            )

            updated_versions = tuple(
                updated_version
                if item.quote_version_id
                == version.quote_version_id
                else item
                for item in quote.versions
            )

            updated_quote = replace(
                quote,
                current_status=(
                    QuoteStatus.APPROVED
                ),
                approved_version_id=(
                    version.quote_version_id
                ),
                versions=updated_versions,
                events=tuple(events)
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
                QuoteStatus.APPROVED
            )
        except ValueError as error:
            raise InvalidQuoteStateError(
                str(error)
            ) from error

    @staticmethod
    def _validate_offered_version(
        version: QuoteVersion
    ) -> None:

        if version.quote_version_id is None:
            raise InvalidQuoteDataError(
                "Versão negociada precisa estar persistida"
            )

        if version.offered_price is None:
            raise InvalidQuoteDataError(
                "Versão negociada precisa estar ofertada"
            )

        if (
            version.bp02 is None
            or version.tax_rate is None
        ):
            raise InvalidQuoteDataError(
                "Versão negociada não possui "
                "base financeira completa"
            )

        if version.contracted_price is not None:
            raise InvalidQuoteStateError(
                "Versão já possui preço contratado"
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
