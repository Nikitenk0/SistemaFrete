from dataclasses import replace
from datetime import (
    datetime,
    timezone
)

from application.exceptions import (
    FreightAlreadyExistsError,
    InvalidFreightDataError,
    QuoteNotFoundError
)
from application.ports.freight_unit_of_work import (
    FreightUnitOfWorkFactory
)
from domain.freight_quote_linking import (
    link_complementary_quotes_to_freight
)
from domain.models.freight import (
    Freight,
    FreightStatus
)
from domain.models.freight_event import (
    FreightEvent,
    FreightEventType
)
from domain.models.quote import (
    Quote,
    QuoteStatus,
    QuoteType
)


class CreateFreightFromApprovedQuote:

    def __init__(
        self,
        freight_unit_of_work_factory:
            FreightUnitOfWorkFactory
    ):
        self._freight_unit_of_work_factory = (
            freight_unit_of_work_factory
        )

    def execute(
        self,
        primary_quote_id: int,
        created_by: int | None = None
    ) -> Freight:

        if primary_quote_id < 1:
            raise InvalidFreightDataError(
                "primary_quote_id inválido"
            )

        with (
            self._freight_unit_of_work_factory.create()
            as unit_of_work
        ):

            quote = (
                unit_of_work.quotes
                .get_by_id_for_update(
                    primary_quote_id
                )
            )

            if quote is None:
                raise QuoteNotFoundError(
                    "Orçamento principal não encontrado"
                )

            self._validate_quote(
                quote
            )

            now = datetime.now(
                timezone.utc
            )

            try:
                created_event = FreightEvent(
                    event_type=(
                        FreightEventType.CREATED
                    ),
                    previous_status=None,
                    new_status=(
                        FreightStatus.PENDING
                    ),
                    occurred_at=now,
                    user_id=created_by
                )

                freight = Freight(
                    customer_id=quote.customer_id,
                    primary_quote_id=quote.quote_id,
                    current_status=(
                        FreightStatus.PENDING
                    ),
                    events=(
                        created_event,
                    ),
                    created_at=now,
                    created_by=created_by
                )
            except ValueError as error:
                raise InvalidFreightDataError(
                    str(error)
                ) from error

            created_freight = (
                unit_of_work.freights.add(
                    freight
                )
            )

            updated_quote = replace(
                quote,
                freight_id=(
                    created_freight.freight_id
                )
            )

            saved_primary_quote = (
                unit_of_work.quotes.save(
                    updated_quote
                )
            )

            complementary_quotes = (
                unit_of_work.quotes
                .list_by_primary_quote_id_for_update(
                    primary_quote_id
                )
            )

            try:
                linked_quotes = (
                    link_complementary_quotes_to_freight(
                        saved_primary_quote,
                        complementary_quotes,
                        created_freight.freight_id
                    )
                )
            except ValueError as error:
                raise InvalidFreightDataError(
                    str(error)
                ) from error

            for original, linked in zip(
                complementary_quotes,
                linked_quotes
            ):
                if original.freight_id == linked.freight_id:
                    continue

                unit_of_work.quotes.save(
                    linked
                )

            unit_of_work.commit()

            return created_freight

    @staticmethod
    def _validate_quote(
        quote: Quote
    ) -> None:

        if quote.quote_type != QuoteType.PRIMARY:
            raise InvalidFreightDataError(
                "Frete só pode ser criado a partir "
                "de orçamento principal"
            )

        if quote.current_status != QuoteStatus.APPROVED:
            raise InvalidFreightDataError(
                "Frete só pode ser criado a partir "
                "de orçamento principal aprovado"
            )

        if quote.freight_id is not None:
            raise FreightAlreadyExistsError(
                "O orçamento principal já possui "
                "um frete associado"
            )
