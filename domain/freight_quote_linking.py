from dataclasses import replace

from domain.models.quote import (
    Quote,
    QuoteType
)


def link_complementary_quotes_to_freight(
    primary_quote: Quote,
    complementary_quotes: tuple[Quote, ...],
    freight_id: int
) -> tuple[Quote, ...]:

    if freight_id < 1:
        raise ValueError(
            "freight_id inválido"
        )

    if primary_quote.quote_id is None:
        raise ValueError(
            "Orçamento principal precisa estar persistido"
        )

    if primary_quote.quote_type != QuoteType.PRIMARY:
        raise ValueError(
            "Orçamento informado não é principal"
        )

    if primary_quote.freight_id != freight_id:
        raise ValueError(
            "Frete não corresponde ao orçamento principal"
        )

    linked_quotes: list[Quote] = []

    for quote in complementary_quotes:

        if quote.quote_id is None:
            raise ValueError(
                "Orçamento complementar precisa estar persistido"
            )

        if quote.quote_type != QuoteType.COMPLEMENTARY:
            raise ValueError(
                "Somente orçamentos complementares podem ser vinculados"
            )

        if quote.primary_quote_id != primary_quote.quote_id:
            raise ValueError(
                "Complementar não pertence ao orçamento principal"
            )

        if quote.customer_id != primary_quote.customer_id:
            raise ValueError(
                "Complementar possui cliente diferente do principal"
            )

        if (
            quote.freight_id is not None
            and quote.freight_id != freight_id
        ):
            raise ValueError(
                "Complementar já pertence a outro frete"
            )

        if quote.freight_id == freight_id:
            linked_quotes.append(
                quote
            )
            continue

        linked_quotes.append(
            replace(
                quote,
                freight_id=freight_id
            )
        )

    return tuple(
        linked_quotes
    )
