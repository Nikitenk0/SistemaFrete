from dataclasses import replace
from datetime import (
    datetime,
    timedelta,
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


class OfferQuote:

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
        validity_days: int,
        offered_price: Decimal | None = None,
        price_change_reason: str | None = None,
        user_id: int | None = None
    ) -> Quote:

        if validity_days < 0:
            raise InvalidQuoteDataError(
                "Validade do orçamento inválida"
            )

        reason = self._clean_optional_text(
            price_change_reason
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

            self._validate_can_offer(
                quote
            )

            version = self._latest_version(
                quote
            )

            self._validate_calculated_version(
                version
            )

            price = (
                offered_price
                if offered_price is not None
                else version.rounded_price
            )

            if price is None:
                raise InvalidQuoteDataError(
                    "Preço ofertado não pôde ser definido"
                )

            if price < 0:
                raise InvalidQuoteDataError(
                    "Preço ofertado não pode ser negativo"
                )

            standard_price = (
                version.rounded_price
            )

            if (
                price != standard_price
                and not reason
            ):
                raise InvalidQuoteDataError(
                    "Alteração do preço ofertado "
                    "exige justificativa"
                )

            try:
                (
                    offered_margin_value,
                    offered_margin_rate
                ) = calculate_effective_margin(
                    gross_price=price,
                    bp02=version.bp02,
                    tax_rate=version.tax_rate
                )
            except ValueError as error:
                raise InvalidQuoteDataError(
                    str(error)
                ) from error

            updated_version = replace(
                version,
                offered_price=price,
                offered_margin_value=(
                    offered_margin_value
                ),
                offered_margin_rate=(
                    offered_margin_rate
                ),
                validity_days_snapshot=(
                    validity_days
                ),
                valid_until=(
                    now.date()
                    + timedelta(
                        days=validity_days
                    )
                )
            )

            events = list(
                quote.events
            )

            if price != standard_price:
                events.append(
                    QuoteEvent(
                        event_type=(
                            QuoteEventType.PRICE_CHANGED
                        ),
                        quote_version_id=(
                            version.quote_version_id
                        ),
                        previous_amount=(
                            standard_price
                        ),
                        new_amount=price,
                        observation=reason,
                        user_id=user_id,
                        occurred_at=now
                    )
                )

            events.append(
                QuoteEvent(
                    event_type=(
                        QuoteEventType.OFFERED
                    ),
                    quote_version_id=(
                        version.quote_version_id
                    ),
                    previous_status=(
                        quote.current_status
                    ),
                    new_status=(
                        QuoteStatus.OFFERED
                    ),
                    new_amount=price,
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
                    QuoteStatus.OFFERED
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
    def _validate_can_offer(
        quote: Quote
    ) -> None:

        try:
            validate_quote_transition(
                quote.current_status,
                QuoteStatus.OFFERED
            )
        except ValueError as error:
            raise InvalidQuoteStateError(
                str(error)
            ) from error

    @staticmethod
    def _validate_calculated_version(
        version: QuoteVersion
    ) -> None:

        if version.quote_version_id is None:
            raise InvalidQuoteDataError(
                "Versão calculada precisa estar persistida"
            )

        required_values = (
            version.bp02,
            version.tax_rate,
            version.calculated_price,
            version.rounded_price
        )

        if any(
            value is None
            for value in required_values
        ):
            raise InvalidQuoteDataError(
                "Versão ainda não possui cálculo completo"
            )

        if version.offered_price is not None:
            raise InvalidQuoteStateError(
                "Versão já foi ofertada"
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

        cleaned = value.strip()

        return cleaned or None
