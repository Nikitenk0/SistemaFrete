from application.exceptions import (
    InvalidFreightDataError,
    QuoteNotFoundError
)
from application.ports.freight_unit_of_work import (
    FreightUnitOfWorkFactory
)
from domain.freight_quote_linking import (
    link_complementary_quotes_to_freight
)
from domain.models.quote import (
    Quote,
    QuoteStatus,
    QuoteType
)


class LinkComplementaryQuotesToFreight:

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
        primary_quote_id: int
    ) -> tuple[Quote, ...]:

        if primary_quote_id < 1:
            raise InvalidFreightDataError(
                "primary_quote_id inválido"
            )

        with (
            self._freight_unit_of_work_factory.create()
            as unit_of_work
        ):

            primary_quote = (
                unit_of_work.quotes
                .get_by_id_for_update(
                    primary_quote_id
                )
            )

            if primary_quote is None:
                raise QuoteNotFoundError(
                    "Orçamento principal não encontrado"
                )

            self._validate_primary_quote(
                primary_quote
            )

            freight = (
                unit_of_work.freights.get_by_id(
                    primary_quote.freight_id
                )
            )

            if freight is None:
                raise InvalidFreightDataError(
                    "Frete associado ao orçamento não foi encontrado"
                )

            if (
                freight.primary_quote_id
                != primary_quote.quote_id
                or freight.customer_id
                != primary_quote.customer_id
            ):
                raise InvalidFreightDataError(
                    "Vínculo entre frete e orçamento principal é inconsistente"
                )

            complementary_quotes = (
                unit_of_work.quotes
                .list_by_primary_quote_id_for_update(
                    primary_quote.quote_id
                )
            )

            try:
                linked_quotes = (
                    link_complementary_quotes_to_freight(
                        primary_quote,
                        complementary_quotes,
                        freight.freight_id
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

            return linked_quotes

    @staticmethod
    def _validate_primary_quote(
        quote: Quote
    ) -> None:

        if quote.quote_type != QuoteType.PRIMARY:
            raise InvalidFreightDataError(
                "Orçamento informado não é principal"
            )

        if quote.current_status != QuoteStatus.APPROVED:
            raise InvalidFreightDataError(
                "Orçamento principal precisa estar aprovado"
            )

        if quote.freight_id is None:
            raise InvalidFreightDataError(
                "Orçamento principal ainda não possui frete"
            )
